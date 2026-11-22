const P = require("../build/pure.js");
let fail = 0;
const eq = (name, got, want) => { const ok = JSON.stringify(got) === JSON.stringify(want); if (!ok) fail++; console.log((ok ? "PASS " : "FAIL ") + name + (ok ? "" : `\n   got:  ${JSON.stringify(got)}\n   want: ${JSON.stringify(want)}`)); };
const rt = (code, opts) => P.serialize(P.parseCode(code).runs, opts);
// round trips keep meaning and stay minimal
eq("plain", rt("Hello"), "Hello");
eq("bold", rt("<b>Hi</b> there"), "<b>Hi</b> there");
eq("nested", rt("<size=20><color=#ff0000>Big <b>red</b></color></size>"), "<size=20><color=red>Big <b>red</b></color></size>");
eq("names off", rt("<color=#ff0000>x</color>", { names: false }), "<color=#ff0000>x</color>");
eq("merge redundant", rt("<color=red>a</color><color=red>b</color>"), "<color=red>ab</color>");
eq("spaces merge", rt("<color=#ff3d8b>one</color> <color=#ff3d8b>two</color>"), "<color=#ff3d8b>one two</color>");
eq("spaces kept when off", rt("<color=#ff3d8b>one</color> <color=#ff3d8b>two</color>", { mergeSpaces: false }), "<color=#ff3d8b>one</color> <color=#ff3d8b>two</color>");
eq("3-digit hex", rt("<color=#f00>x</color>"), "<color=red>x</color>");
eq("persistence order", rt("<b><color=#123456>ab</color>cd</b>"), "<b><color=#123456>ab</color>cd</b>");
eq("outer longest", P.serialize([{t:"ab",b:true,i:false,c:"#123456",s:null},{t:"cd",b:false,i:false,c:"#123456",s:null}]), "<color=#123456><b>ab</b>cd</color>");
// counting: newlines count twice
eq("charCount", P.charCount("a\nb"), 4);
eq("byteCount", P.byteCount("♥\n"), 5);
// parser warnings
const w = P.parseCode("<b>open <color=zzz>x</color> <u>u</u>").warnings;
eq("warnings", w.length, 3);
eq("bad close", P.parseCode("x</b>").warnings.length, 1);
// editing ops
let r = P.parseCode("Hello world").runs;
r = P.mapRange(r, 0, 5, (x) => ({ ...x, b: true }));
eq("mapRange", P.serialize(r), "<b>Hello</b> world");
r = P.insertRuns(r, 5, [{ t: "!", b: false, i: false, c: null, s: null }]);
eq("insert", P.serialize(r), "<b>Hello</b>! world");
r = P.deleteRange(r, 0, 2);
eq("delete", P.serialize(r), "<b>llo</b>! world");
eq("fmtAt", P.fmtAt(r, 2).b, true);
// gradient: 2 steps per word over "ab cd"
let g = P.gradientRuns(P.parseCode("ab cd").runs, 0, 5, ["#ff0000", "#0000ff"], "word", 2);
eq("gradient word", P.serialize(g), "<color=red>ab </color><color=blue>cd</color>");
g = P.gradientRuns(P.parseCode("abcd").runs, 0, 4, ["#ff0000", "#0000ff"], "letter", 2);
eq("gradient bands", P.serialize(g), "<color=red>ab</color><color=blue>cd</color>");
g = P.gradientRuns(P.parseCode("x♥y").runs, 0, 3, ["#ff0000", "#0000ff"], "letter", 3);
eq("gradient surrogate-safe text", P.textOf(g), "x♥y");
// official presets round-trip within limits
const preset = "<b><size=60><color=#F6F6F6>✬</color></size> <size=36><color=#16C326>Merry</color> <color=#EA4630>Christmas</color></size><size=60><color=#F6F6F6>✬</color></size></b>";
const out = rt(preset);
console.log("preset in:", preset.length, "out:", out.length, "\n  ", out);
eq("preset text kept", P.textOf(P.parseCode(out).runs), P.textOf(P.parseCode(preset).runs));

// ---- AI helpers ----
const sys = P.aiSystem({ mode: "profile", limit: 1000 });
eq("system names the limit", /under 1000/.test(sys), true);
eq("system lists only game tags", /<color=#ff3d8b>/.test(sys) && !/<u>/.test(sys), true);
eq("gift system mentions bytes + %username%", /255 bytes/.test(P.aiSystem({ mode: "gift", limit: 240, bytes: 255 })) && /%username%/.test(P.aiSystem({ mode: "gift", limit: 240, bytes: 255 })), true);
const tp = P.aiPrompt("translate", { mode: "profile", lang: "French", code: "<b>Hi</b>" });
eq("prompt wraps code", tp.includes("-----BEGIN-----\n<b>Hi</b>\n-----END-----"), true);
eq("partial note", /one part of a longer text/.test(P.aiPrompt("fix", { mode: "profile", code: "x", partial: true })), true);
eq("write prompt carries brief", /loves cats/.test(P.aiPrompt("write", { mode: "gift", brief: "loves cats", tone: "Cute", theme: "Ocean", lang: "English", target: 150 })), true);
eq("cleanReply fence", P.cleanReply("```\n<b>x</b>\n```"), "<b>x</b>");
eq("cleanReply markers", P.cleanReply("-----BEGIN-----\nhey\n-----END-----"), "hey");
eq("cleanReply keeps inner newlines", P.cleanReply("  a\n\nb  "), "a\n\nb");
const ep = P.aiPrompt("edit", { mode: "profile", code: "<b>Hi</b>", partial: true, instruction: "make it rhyme" });
eq("edit prompt carries instruction + part", /make it rhyme/.test(ep) && /one part of a longer text/.test(ep) && ep.includes("<b>Hi</b>"), true);
const ip = P.aiPrompt("insert", { mode: "profile", before: "<b>Top</b>\n", after: "\nBye", instruction: "a hobbies line", target: 120 });
eq("insert prompt marks the spot", ip.includes("<b>Top</b>\n" + P.AI_MARK + "\nBye") && /a hobbies line/.test(ip) && /about 120/.test(ip), true);
eq("cleanReply drops the marker", P.cleanReply(`${P.AI_MARK}new line`), "new line");
const split = P.sseSplitter();
eq("sse partial", split('data: {"a":1}\ndata: {"b"'), ['{"a":1}']);
eq("sse rest + done", split(':2}\r\n\ndata: [DONE]\n'), ['{"b":2}']);
eq("pick anthropic", P.pickModel("anthropic", ["claude-haiku-4-5", "claude-opus-5-5"]), "claude-opus-5-5");
eq("pick openai", P.pickModel("openai", ["gpt-4o", "gpt-5.1", "gpt-5.1-mini", "gpt-5", "whisper-1", "gpt-5.1-codex"]), "gpt-5.1");
eq("pick gemini", P.pickModel("gemini", ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-pro-preview", "text-embedding-004"]), "gemini-2.5-pro");
// every template (hand-made and generated) must parse cleanly and fit the game's limits;
// gift templates may only use symbols that show in gifts
{
  const fs = require("fs"), path = require("path");
  const root = path.join(__dirname, "..");
  const sym = JSON.parse(fs.readFileSync(path.join(root, "src/symbols.json"), "utf8"));
  const po = new Set(sym.profileOnly.flatMap((x) => [...x]));
  const lib = JSON.parse(fs.readFileSync(path.join(root, "src/templates.json"), "utf8"));
  const src = fs.readFileSync(path.join(root, "src/profile-studio.html"), "utf8");
  const block = src.slice(src.indexOf("const TEMPLATES = {"), src.indexOf("\n};", src.indexOf("const TEMPLATES = {")) + 3);
  const featured = new Function(block.replace("const TEMPLATES = ", "return ").replace(/;\s*$/, ""))();
  const bad = [];
  for (const mode of ["profile", "gift"]) {
    for (const t of [...featured[mode], ...lib[mode]]) {
      const p = P.parseCode(t.code), code = P.serialize(p.runs, { names: true, mergeSpaces: true });
      const why = p.warnings.length ? "warnings" : P.charCount(code) > (mode === "gift" ? 240 : 1000) ? "too long"
        : mode === "gift" && P.byteCount(code) > 255 ? "too many bytes"
        : mode === "gift" && [...code].some((ch) => po.has(ch)) ? "symbol not shown in gifts" : "";
      if (why) bad.push(`${mode} ${t.name}: ${why}`);
    }
  }
  eq(`all ${featured.profile.length + lib.profile.length} profile + ${featured.gift.length + lib.gift.length} gift templates fit`, bad, []);
}
console.log(fail ? `${fail} FAILED` : "ALL PASS");
