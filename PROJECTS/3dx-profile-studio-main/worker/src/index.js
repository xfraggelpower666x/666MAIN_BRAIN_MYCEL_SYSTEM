// Free built-in AI for 3DX Profile Studio (Cloudflare Worker).
//
// The page POSTs { system, prompt } to /v1/write. This Worker runs it on Workers AI (Cloudflare's own
// models: no key, no AI vendor account), applies limits, and streams the reply back as server-sent events:
//   data: {"t":"<text so far>"}            text as it arrives (whole text, like the page expects)
//   data: {"done":true,"stop":"end_turn"}  finished (stop: end_turn, max_tokens or refusal)
//   data: {"error":{"code":"rate","message":"..."}}
// A daily neuron cap keeps it inside Workers AI's free daily allowance (10,000 neurons, reset at 00:00 UTC),
// so it never bills past it. Nothing is stored or logged: a timestamp per visitor IP for the rate limit
// (kept one minute) and the day's neuron total.

import { DurableObject } from "cloudflare:workers";

const MAX_SYSTEM_CHARS = 30000;
const MAX_PROMPT_CHARS = 30000;
const NEURON_USD = 0.011 / 1000;   // Workers AI: $0.011 per 1,000 neurons

// One Limiter instance per key ("ip:1.2.3.4", "neurons:2026-11-22"); each counts its own hits exactly.
export class Limiter extends DurableObject {
  async take(limit, windowMs) {
    const now = Date.now();
    const hits = ((await this.ctx.storage.get("hits")) || []).filter((t) => now - t < windowMs);
    if (hits.length >= limit) return false;
    hits.push(now);
    await this.ctx.storage.put("hits", hits);
    await this.ctx.storage.setAlarm(now + windowMs);   // forget this visitor once the window has passed
    return true;
  }
  // The day's neuron total
  async used() {
    return (await this.ctx.storage.get("used")) || 0;
  }
  async spend(n) {
    const used = ((await this.ctx.storage.get("used")) || 0) + n;
    await this.ctx.storage.put("used", used);
    if (!(await this.ctx.storage.getAlarm())) await this.ctx.storage.setAlarm(Date.now() + 2 * 86_400_000);
    return used;
  }
  async alarm() {
    await this.ctx.storage.deleteAll();
  }
}

const stub = (env, key) => env.LIMITS.get(env.LIMITS.idFromName(key));

async function take(env, key, limit, windowMs) {
  if (!env.LIMITS) return true;
  try {
    return await stub(env, key).take(limit, windowMs);
  } catch (e) {
    console.log("limiter error:", String(e));
    return true;   // a limiter outage shouldn't take the AI down
  }
}

const today = () => new Date().toISOString().slice(0, 10);   // UTC, like the free allowance

async function neuronsUsed(env) {
  try { return env.LIMITS ? await stub(env, `neurons:${today()}`).used() : 0; }
  catch (e) { console.log("budget error:", String(e)); return 0; }
}

async function spendNeurons(env, n) {
  try { if (env.LIMITS && n > 0) await stub(env, `neurons:${today()}`).spend(n); }
  catch (e) { console.log("budget error:", String(e)); }
}

// Neurons for one answer: Workers AI's own count when it gives one, else from the tokens and the model's price,
// else from the length of the text (about 3.5 characters a token)
function neuronsFor(usage, env, inChars, outChars) {
  if (usage && Number(usage.neurons) > 0) return Number(usage.neurons);
  const tin = Number(usage?.prompt_tokens) || inChars / 3.5;
  const tout = Number(usage?.completion_tokens) || outChars / 3.5;
  const usd = (tin * (Number(env.PRICE_IN) || 0.3) + tout * (Number(env.PRICE_OUT) || 1.2)) / 1e6;
  return usd / NEURON_USD;
}

function corsHeaders(origin, env) {
  const allowed = (env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  return allowed.includes(origin) ? { "Access-Control-Allow-Origin": origin, "Vary": "Origin" } : null;
}

function json(status, body, cors) {
  return new Response(JSON.stringify(body), {
    status, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...(cors || {}) },
  });
}
const fail = (status, code, message, cors) => json(status, { error: { code, message } }, cors);

const BUSY = "The free AI is busy right now. Wait a minute and try again, or add your own key in AI settings.";
const SPENT = "The free AI has used up today's allowance. It's back at midnight UTC, or add your own key in AI settings.";

// Plain messages for players; never pass account details through
function describe(e) {
  const m = String(e?.message || e);
  console.log("workers ai error", m.slice(0, 300));   // never the player's text (wrangler tail shows it)
  if (/capacity|rate|too many|3040|429/i.test(m)) return { code: "rate", message: BUSY };
  if (/network|connection|fetch failed/i.test(m)) return { code: "network", message: "Couldn't reach the AI. Try again in a moment." };
  if (/invalid input|too long|context|8001|5021/i.test(m)) return { code: "api", message: "The AI couldn't use that request. Select less, or try different wording." };
  return { code: "unavailable", message: "The free AI isn't working right now. Try again later, or add your own key in AI settings." };
}

// Workers AI streams server-sent events: OpenAI-style chunks for most models, { response } for older ones
function sseLines() {
  let buf = "";
  return (chunk) => {
    buf += chunk;
    const out = [];
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).replace(/\r$/, "");
      buf = buf.slice(i + 1);
      if (line.startsWith("data:")) { const d = line.slice(5).trim(); if (d && d !== "[DONE]") out.push(d); }
    }
    return out;
  };
}
const STOPS = { stop: "end_turn", length: "max_tokens", content_filter: "refusal" };

// Feedback from the page becomes a GitHub issue (public), filed with a token that can only write issues
const KINDS = { bug: "Bug", idea: "Idea", other: "Feedback" };
const unping = (s) => s.replace(/@/g, "@​");          // no @mentions from strangers
const fence = (s) => "```\n" + s.replace(/```/g, "`​``") + "\n```";

async function feedback(request, env, cors) {
  if (!env.GITHUB_TOKEN || !env.FEEDBACK_REPO) return fail(503, "unavailable", "Feedback isn't set up yet.", cors);
  let b;
  try { b = await request.json(); } catch { return fail(400, "api", "Bad request.", cors); }
  if (b.website) return json(200, { ok: true }, cors);       // honeypot field: bots fill it, people never see it
  const kind = KINDS[b.kind] ? b.kind : "other";
  const message = typeof b.message === "string" ? b.message.trim() : "";
  const contact = typeof b.contact === "string" ? b.contact.trim().slice(0, 100) : "";
  const sample = typeof b.sample === "string" ? b.sample.slice(0, 1500) : "";
  const version = String(b.version || "").slice(0, 20), mode = String(b.mode || "").slice(0, 20);
  if (message.length < 5) return fail(400, "api", "Tell us a little more first.", cors);
  if (message.length > 4000) return fail(413, "api", "That's a bit long. Keep it under 4000 characters.", cors);

  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  if (!(await take(env, `fb:${ip}`, 3, 3_600_000))) return fail(429, "rate", "Thanks! You've sent a few already. Try again in an hour.", cors);
  if (!(await take(env, `fbday:${today()}`, 50, 86_400_000))) {
    return fail(429, "rate", "We've had lots of feedback today. Please try again tomorrow.", cors);
  }

  const first = message.split("\n")[0].slice(0, 70);
  const lines = [unping(message), "", "---",
                 `**From:** ${contact ? unping(contact) : "anonymous"} · **Version:** ${version || "?"} · **Mode:** ${mode || "?"}`];
  if (sample) lines.push("", "<details><summary>Their text</summary>", "", fence(sample), "", "</details>");
  lines.push("", "<sub>Sent with the Feedback button in 3DX Profile Studio.</sub>");

  let res;
  try {
    res = await fetch(`https://api.github.com/repos/${env.FEEDBACK_REPO}/issues`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${env.GITHUB_TOKEN}`, "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "3dx-profile-studio-feedback",
                 "Content-Type": "application/json" },
      body: JSON.stringify({ title: `${KINDS[kind]}: ${unping(first)}`, body: lines.join("\n"), labels: ["feedback", kind] }),
    });
  } catch {
    return fail(502, "network", "Couldn't send your feedback. Try again in a moment.", cors);
  }
  if (!res.ok) {
    console.log("github error", res.status, (await res.text()).slice(0, 300));
    return fail(502, "unavailable", "Couldn't send your feedback right now. Try again later.", cors);
  }
  const issue = await res.json();
  return json(200, { ok: true, number: issue.number, url: issue.html_url }, cors);
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const cors = corsHeaders(request.headers.get("Origin") || "", env);

    if (request.method === "OPTIONS") {
      if (!cors) return new Response(null, { status: 403 });
      return new Response(null, {
        status: 204,
        headers: { ...cors, "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                   "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Max-Age": "86400" },
      });
    }
    if (request.method === "GET" && url.pathname === "/") {
      const cap = Number(env.NEURON_DAILY) || 0;
      return json(200, { ok: true, service: "3dx-profile-studio-ai", model: env.MODEL, ready: !!env.AI,
                         today: cap ? { used: Math.round(await neuronsUsed(env)), cap } : undefined,
                         feedback: !!env.GITHUB_TOKEN }, { "Access-Control-Allow-Origin": "*" });
    }
    if (request.method === "POST" && url.pathname === "/v1/feedback") {
      if (!cors) return fail(403, "unavailable", "Feedback only works inside 3DX Profile Studio.", null);
      return feedback(request, env, cors);
    }
    if (request.method !== "POST" || url.pathname !== "/v1/write") return fail(404, "api", "Not found.", cors);
    if (!cors) return fail(403, "unavailable", "This free AI only works inside 3DX Profile Studio.", null);
    if (!env.AI) return fail(503, "unavailable", "The free AI isn't set up yet.", cors);

    // Exact limits (Durable Objects): per visitor per minute, requests per day, and the free neuron allowance
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    if (!(await take(env, `ip:${ip}`, Number(env.PER_MINUTE) || 10, 60_000))) return fail(429, "rate", BUSY, cors);
    const daily = Number(env.DAILY_LIMIT) || 0;
    if (daily && !(await take(env, `day:${today()}`, daily, 86_400_000))) return fail(429, "rate", SPENT, cors);
    const cap = Number(env.NEURON_DAILY) || 0;
    if (cap && (await neuronsUsed(env)) >= cap) return fail(429, "rate", SPENT, cors);

    let body;
    try { body = await request.json(); } catch { return fail(400, "api", "Bad request.", cors); }
    const system = typeof body.system === "string" ? body.system : "";
    const prompt = typeof body.prompt === "string" ? body.prompt : "";
    if (!prompt.trim()) return fail(400, "api", "Nothing to write about yet.", cors);
    if (system.length > MAX_SYSTEM_CHARS || prompt.length > MAX_PROMPT_CHARS) {
      return fail(413, "api", "That's too much text for the free AI. Select less, or add your own key in AI settings.", cors);
    }

    const params = { messages: [{ role: "system", content: system }, { role: "user", content: prompt }],
                     max_completion_tokens: Number(env.MAX_TOKENS) || 4000, stream: true,
                     stream_options: { include_usage: true } };
    if (env.REASONING) params.reasoning_effort = env.REASONING;

    const { readable, writable } = new TransformStream();
    const writer = writable.getWriter();
    const enc = new TextEncoder();
    const send = (obj) => writer.write(enc.encode(`data: ${JSON.stringify(obj)}\n\n`));

    const pump = (async () => {
      let text = "", usage = null, stop = "", reader = null;
      try {
        const stream = await env.AI.run(env.MODEL, params);
        reader = stream.getReader();
        const split = sseLines(), dec = new TextDecoder();
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          for (const d of split(dec.decode(value, { stream: true }))) {
            let j;
            try { j = JSON.parse(d); } catch { continue; }
            if (j.usage) usage = j.usage;
            const c = j.choices?.[0];
            const piece = c?.delta?.content ?? (typeof j.response === "string" ? j.response : "");
            if (c?.finish_reason) stop = STOPS[c.finish_reason] || "end_turn";
            if (piece) { text += piece; await send({ t: text }); }
          }
        }
        await send({ done: true, stop: stop || "end_turn" });
      } catch (e) {
        try { await reader?.cancel(); } catch { /* already closed */ }
        try { await send({ error: describe(e) }); } catch { /* player already left */ }
      } finally {
        if (usage || text) await spendNeurons(env, neuronsFor(usage, env, system.length + prompt.length, text.length));
        try { await writer.close(); } catch { /* already closed */ }
      }
    })();
    ctx.waitUntil(pump);

    return new Response(readable, {
      status: 200, headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-store", ...cors },
    });
  },
};
