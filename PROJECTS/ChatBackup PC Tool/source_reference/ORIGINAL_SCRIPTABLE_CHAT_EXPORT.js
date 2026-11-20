const CONFIG = {
  OUTPUT_FOLDER: "ChatGPT_MD_Exports",
  INCLUDE_TOOL_MESSAGES: false,
  INCLUDE_MESSAGE_TIMESTAMPS: false,
  INCLUDE_EXPORT_INTEGRITY_SECTION: true,
  REMOVE_CHATGPT_CITATION_MARKERS: true,
  SHOW_SUCCESS_ALERT: true,
  OPEN_IOS_SHARE_SHEET_AFTER_SAVE: false,
  REQUEST_TIMEOUT_SECONDS: 60,
  DOWNLOAD_RETRIES: 3,
  DOM_RENDER_WAIT_ATTEMPTS: 20,
  DOM_RENDER_WAIT_MS: 500
};

await main();
Script.complete();

async function main() {
  try {
    const inputUrl = await resolveInputUrl();
    const url = normalizeAndValidateShareUrl(inputUrl);

    let chat;

    try {
      const html = await fetchSharePageWithRetry(url);
      chat = parseSharedConversation(html, url);
    } catch (primaryError) {
      console.warn(
        "Direktexport fehlgeschlagen, DOM-Fallback: " +
        primaryError.message
      );

      chat = await extractRenderedConversationWithWebView(url);

      if (!Array.isArray(chat.warnings)) {
        chat.warnings = [];
      }

      chat.warnings.push(
        "DOM-Fallback verwendet: Formatierungen, Links oder Anhänge können unvollständig sein."
      );
    }

    if (
      !chat ||
      !Array.isArray(chat.messages) ||
      chat.messages.length === 0
    ) {
      throw new Error(
        "Im Share-Link wurden keine sichtbaren Nachrichten gefunden. " +
        "Erstelle den Link über den Teilen-Button oben im Chat."
      );
    }

    finalizeChatStats(chat);

    const markdown = buildMarkdown(chat, url);
    const saveResult = saveMarkdownFile(chat, markdown);

    if (CONFIG.OPEN_IOS_SHARE_SHEET_AFTER_SAVE) {
      await ShareSheet.present([saveResult.filePath]);
    }

    if (CONFIG.SHOW_SUCCESS_ALERT) {
      await showSuccess(
        saveResult.filePath,
        chat.messages.length,
        chat
      );
    }
  } catch (error) {
    await showError(error);
  }
}

// -----------------------------------------------------------------------------
// Eingabe
// -----------------------------------------------------------------------------

async function resolveInputUrl() {
  const candidates = [];

  if (Array.isArray(args.urls)) {
    candidates.push.apply(candidates, args.urls);
  }

  if (Array.isArray(args.plainTexts)) {
    candidates.push.apply(candidates, args.plainTexts);
  }

  if (typeof args.shortcutParameter === "string") {
    candidates.push(args.shortcutParameter);
  }

  const clipboard = Pasteboard.pasteString();

  if (clipboard) {
    candidates.push(clipboard);
  }

  for (const candidate of candidates) {
    const url = findChatGptUrl(String(candidate || ""));

    if (url) {
      return url;
    }
  }

  const prompt = new Alert();

  prompt.title = "ChatGPT-Share-Link";
  prompt.message =
    "Kein Link wurde aus dem Teilen-Menü übergeben. " +
    "Füge einen öffentlichen ChatGPT-Share-Link ein.";

  prompt.addTextField(
    "https://chatgpt.com/share/...",
    ""
  );

  prompt.addAction("Exportieren");
  prompt.addCancelAction("Abbrechen");

  const result = await prompt.presentAlert();

  if (result === -1) {
    throw new Error("Export abgebrochen.");
  }

  const manualUrl = findChatGptUrl(
    prompt.textFieldValue(0)
  );

  if (!manualUrl) {
    throw new Error(
      "Kein gültiger ChatGPT-Link eingegeben."
    );
  }

  return manualUrl;
}

function findChatGptUrl(text) {
  const matches = text.match(
    /https?:\/\/(?:www\.)?(?:chatgpt\.com|chat\.openai\.com)\/[^\s<>"']+/gi
  );

  if (!matches || matches.length === 0) {
    return null;
  }

  for (const match of matches) {
    const cleaned = match.replace(
      /[),.;!?]+$/g,
      ""
    );

    if (
      /\/(?:share|s)\//i.test(cleaned) ||
      /\/c\//i.test(cleaned)
    ) {
      return cleaned;
    }
  }

  return matches[0].replace(
    /[),.;!?]+$/g,
    ""
  );
}

function normalizeAndValidateShareUrl(rawUrl) {
  let url = String(rawUrl || "")
    .trim()
    .replace(/^http:\/\//i, "https://");

  url = url.split("#")[0];

  if (
    !/^https:\/\/(?:www\.)?(?:chatgpt\.com|chat\.openai\.com)\//i.test(url)
  ) {
    throw new Error(
      "Der Link gehört nicht zu ChatGPT."
    );
  }

  if (/\/c\//i.test(url)) {
    throw new Error(
      "Das ist ein privater Chat-Link (/c/...). " +
      "Scriptable kann die ChatGPT-Anmeldung aus Safari nicht übernehmen. " +
      "Öffne den Chat, tippe oben auf „Teilen“, erstelle den öffentlichen " +
      "Share-Link und teile diesen an das Skript."
    );
  }

  if (!/\/(?:share|s)\//i.test(url)) {
    throw new Error(
      "Benötigt wird ein öffentlicher ChatGPT-Share-Link wie " +
      "https://chatgpt.com/share/..."
    );
  }

  return url;
}

// -----------------------------------------------------------------------------
// Download
// -----------------------------------------------------------------------------

async function fetchSharePageWithRetry(url) {
  let lastError = null;
  const retries = Math.max(
    1,
    Number(CONFIG.DOWNLOAD_RETRIES) || 1
  );

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await fetchSharePage(url);
    } catch (error) {
      lastError = error;

      if (attempt < retries) {
        console.warn(
          "Downloadversuch " +
          attempt +
          " fehlgeschlagen: " +
          error.message
        );

        await sleep(attempt * 750);
      }
    }
  }

  throw lastError;
}

async function fetchSharePage(url) {
  const request = makeBrowserLikeRequest(url);
  const html = await request.loadString();

  const status = Number(
    (request.response || {}).statusCode || 0
  );

  if (status && status >= 400) {
    throw new Error(
      "ChatGPT-Share-Seite konnte nicht geladen werden. HTTP " +
      status +
      "."
    );
  }

  if (!html || html.length < 500) {
    throw new Error(
      "Die ChatGPT-Share-Seite war leer oder unvollständig."
    );
  }

  return html;
}

function makeBrowserLikeRequest(url) {
  const request = new Request(url);

  request.method = "GET";
  request.timeoutInterval =
    CONFIG.REQUEST_TIMEOUT_SECONDS;

  request.headers = {
    "User-Agent":
      "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) " +
      "AppleWebKit/605.1.15 (KHTML, like Gecko) " +
      "Version/18.0 Mobile/15E148 Safari/604.1",

    "Accept":
      "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",

    "Accept-Language":
      "de-DE,de;q=0.9,en;q=0.8",

    "Referer":
      "https://chatgpt.com/"
  };

  return request;
}

// -----------------------------------------------------------------------------
// Parser: React-Flight-Format und älteres __NEXT_DATA__
// -----------------------------------------------------------------------------

function parseSharedConversation(html, sourceUrl) {
  let lastError = null;

  try {
    const loaders = extractReactFlightLoaders(html);

    for (let index = 0; index < loaders.length; index++) {
      try {
        const decoded =
          decodeReactFlightLoader(loaders[index]);

        const route =
          findShareRoute(decoded);

        if (!route) {
          continue;
        }

        const serverResponse =
          isObject(route.serverResponse)
            ? route.serverResponse
            : {};

        const data =
          isObject(serverResponse.data)
            ? serverResponse.data
            : (
                isObject(route.data)
                  ? route.data
                  : {}
              );

        const chat = chatFromData(
          data,
          route,
          sourceUrl
        );

        chat.parser = "react-flight";
        chat.parserDetails =
          "React-Flight-Loader " +
          (index + 1) +
          " von " +
          loaders.length;

        return chat;
      } catch (error) {
        lastError = error;
      }
    }
  } catch (error) {
    lastError = error;
  }

  try {
    const legacy =
      extractLegacyNextData(html);

    if (legacy) {
      const chat = chatFromData(
        legacy.data,
        legacy.route,
        sourceUrl
      );

      chat.parser = "legacy-next-data";
      chat.parserDetails =
        "Legacy __NEXT_DATA__";

      return chat;
    }
  } catch (error) {
    lastError = error;
  }

  throw (
    lastError ||
    new Error(
      "Kein unterstütztes Share-Datenformat gefunden."
    )
  );
}

function extractReactFlightLoaders(html) {
  const loaders = [];
  const scripts = extractScriptBodies(html);
  const marker = "streamController.enqueue(";

  for (const script of scripts) {
    if (script.indexOf(marker) === -1) {
      continue;
    }

    let from = 0;

    while (true) {
      const markerIndex =
        script.indexOf(marker, from);

      if (markerIndex === -1) {
        break;
      }

      const argumentStart =
        markerIndex + marker.length;

      const closeIndex =
        script.indexOf(");", argumentStart);

      const quoteIndex =
        script.indexOf('"', argumentStart);

      if (
        quoteIndex !== -1 &&
        (
          closeIndex === -1 ||
          quoteIndex < closeIndex
        )
      ) {
        const literal =
          readJsonStringLiteral(
            script,
            quoteIndex
          );

        if (!literal) {
          from = quoteIndex + 1;
          continue;
        }

        from = literal.endIndex + 1;

        try {
          const chunk = JSON.parse(
            literal.literal
          );

          if (
            typeof chunk === "string" &&
            chunk.trim().charAt(0) === "["
          ) {
            const parsed = JSON.parse(
              chunk.trim()
            );

            if (Array.isArray(parsed)) {
              loaders.push(parsed);
            }
          }
        } catch (_) {
          // Nächsten Datenblock prüfen.
        }
      } else {
        from = argumentStart + 1;
      }
    }
  }

  return loaders;
}

function extractScriptBodies(html) {
  const scripts = [];
  const regex =
    /<script\b[^>]*>([\s\S]*?)<\/script>/gi;

  let match;

  while ((match = regex.exec(html)) !== null) {
    scripts.push(match[1] || "");
  }

  return scripts;
}

function readJsonStringLiteral(text, startIndex) {
  if (text.charAt(startIndex) !== '"') {
    return null;
  }

  let escaped = false;

  for (
    let i = startIndex + 1;
    i < text.length;
    i++
  ) {
    const char = text.charAt(i);

    if (escaped) {
      escaped = false;
    } else if (char === "\\") {
      escaped = true;
    } else if (char === '"') {
      return {
        literal: text.slice(
          startIndex,
          i + 1
        ),
        endIndex: i
      };
    }
  }

  return null;
}

function decodeReactFlightLoader(loader) {
  const cache = new Map();
  const resolving = new Set();

  function decodeKey(rawKey) {
    if (
      typeof rawKey === "string" &&
      /^_\d+$/.test(rawKey)
    ) {
      const index =
        Number(rawKey.slice(1));

      if (
        index >= 0 &&
        index < loader.length &&
        typeof loader[index] === "string"
      ) {
        return loader[index];
      }
    }

    return String(rawKey);
  }

  function resolve(value) {
    if (
      typeof value === "number" &&
      Number.isInteger(value)
    ) {
      if (cache.has(value)) {
        return cache.get(value);
      }

      if (
        value < 0 ||
        value >= loader.length
      ) {
        return value;
      }

      if (resolving.has(value)) {
        return null;
      }

      resolving.add(value);

      const resolved =
        resolve(loader[value]);

      resolving.delete(value);
      cache.set(value, resolved);

      return resolved;
    }

    if (Array.isArray(value)) {
      return value.map(resolve);
    }

    if (isObject(value)) {
      const output = {};

      for (const key of Object.keys(value)) {
        output[decodeKey(key)] =
          resolve(value[key]);
      }

      return output;
    }

    return value;
  }

  const decoded = {};

  for (
    let i = 1;
    i + 1 < loader.length;
    i += 2
  ) {
    const key = loader[i];

    if (
      typeof key === "string" &&
      !Object.prototype.hasOwnProperty.call(
        decoded,
        key
      )
    ) {
      decoded[key] =
        resolve(loader[i + 1]);
    }
  }

  return decoded;
}

function findShareRoute(decoded) {
  if (!isObject(decoded)) {
    return null;
  }

  const loaderData =
    isObject(decoded.loaderData)
      ? decoded.loaderData
      : {};

  const knownKeys = [
    "routes/share.$shareId.($action)",
    "routes/share.$shareId",
    "routes/s.$shareId.($action)",
    "routes/s.$shareId"
  ];

  for (const key of knownKeys) {
    if (isObject(loaderData[key])) {
      return loaderData[key];
    }
  }

  const seen = new Set();

  function search(value, depth) {
    if (
      depth > 10 ||
      !value ||
      typeof value !== "object" ||
      seen.has(value)
    ) {
      return null;
    }

    seen.add(value);

    const directData =
      isObject(value.data)
        ? value.data
        : null;

    const serverData =
      isObject(value.serverResponse) &&
      isObject(value.serverResponse.data)
        ? value.serverResponse.data
        : null;

    if (
      looksLikeConversationData(directData) ||
      looksLikeConversationData(serverData)
    ) {
      return value;
    }

    for (const key of Object.keys(value)) {
      const found =
        search(value[key], depth + 1);

      if (found) {
        return found;
      }
    }

    return null;
  }

  return search(decoded, 0);
}

function looksLikeConversationData(value) {
  return (
    isObject(value) &&
    isObject(value.mapping) &&
    Array.isArray(
      value.linear_conversation
    )
  );
}

function extractLegacyNextData(html) {
  const regex =
    /<script\b[^>]*id=["']__NEXT_DATA__["'][^>]*>([\s\S]*?)<\/script>/i;

  const match = regex.exec(html);

  if (!match) {
    return null;
  }

  const payload = JSON.parse(match[1]);

  const props =
    isObject(payload.props)
      ? payload.props
      : {};

  const pageProps =
    isObject(props.pageProps)
      ? props.pageProps
      : {};

  const serverResponse =
    isObject(pageProps.serverResponse)
      ? pageProps.serverResponse
      : {};

  const data =
    isObject(serverResponse.data)
      ? serverResponse.data
      : {};

  return {
    route: {
      sharedConversationId:
        data.conversation_id ||
        "shared",

      serverResponse: {
        data: data
      }
    },

    data: data
  };
}

function chatFromData(data, route, sourceUrl) {
  if (!isObject(data)) {
    throw new Error(
      "Keine Gesprächsdaten im Share-Link."
    );
  }

  const mapping =
    isObject(data.mapping)
      ? data.mapping
      : {};

  const sequence =
    Array.isArray(
      data.linear_conversation
    )
      ? data.linear_conversation
      : [];

  const messages = [];
  const seenIds = new Set();

  const stats = {
    sourceEntries: sequence.length,
    exported: 0,
    skippedHidden: 0,
    skippedRole: 0,
    skippedRecipient: 0,
    skippedEmpty: 0,
    skippedDuplicate: 0,
    possiblyIncomplete: 0
  };

  for (const entry of sequence) {
    let node = null;

    if (
      isObject(entry) &&
      typeof entry.id === "string" &&
      isObject(mapping[entry.id])
    ) {
      node = mapping[entry.id];
    } else if (
      isObject(entry) &&
      isObject(entry.message)
    ) {
      node = entry;
    }

    if (
      !isObject(node) ||
      !isObject(node.message)
    ) {
      stats.skippedEmpty++;
      continue;
    }

    const message = node.message;

    const metadata =
      isObject(message.metadata)
        ? message.metadata
        : {};

    if (
      metadata.is_visually_hidden_from_conversation ===
      true
    ) {
      stats.skippedHidden++;
      continue;
    }

    const author =
      isObject(message.author)
        ? message.author
        : {};

    const role =
      typeof author.role === "string"
        ? author.role
        : "assistant";

    if (
      role === "system" ||
      role === "developer"
    ) {
      stats.skippedRole++;
      continue;
    }

    if (
      role === "tool" &&
      !CONFIG.INCLUDE_TOOL_MESSAGES
    ) {
      stats.skippedRole++;
      continue;
    }

    const recipient =
      typeof message.recipient === "string"
        ? message.recipient
        : "all";

    if (
      role === "assistant" &&
      recipient !== "all" &&
      recipient !== ""
    ) {
      stats.skippedRecipient++;
      continue;
    }

    const messageId =
      typeof message.id === "string"
        ? message.id
        : "";

    if (
      messageId &&
      seenIds.has(messageId)
    ) {
      stats.skippedDuplicate++;
      continue;
    }

    const content =
      isObject(message.content)
        ? message.content
        : {};

    const text =
      flattenMessageContent(
        content,
        message
      ).trim();

    if (!text) {
      stats.skippedEmpty++;
      continue;
    }

    if (messageId) {
      seenIds.add(messageId);
    }

    const status =
      typeof message.status === "string"
        ? message.status
        : "";

    if (
      role === "assistant" &&
      status &&
      status !== "finished_successfully"
    ) {
      stats.possiblyIncomplete++;
    }

    if (hasUnclosedCodeFence(text)) {
      stats.possiblyIncomplete++;
    }

    messages.push({
      role: role,
      author: authorNameForRole(role),
      text: text,
      createdAt:
        typeof message.create_time ===
        "number"
          ? message.create_time
          : null
    });
  }

  stats.exported = messages.length;

  const model =
    isObject(data.model) &&
    typeof data.model.slug === "string"
      ? data.model.slug
      : "";

  const shareId =
    (
      typeof route.sharedConversationId ===
      "string" &&
      route.sharedConversationId
    ) ||
    (
      typeof data.conversation_id ===
      "string" &&
      data.conversation_id
    ) ||
    extractShareId(sourceUrl) ||
    "shared";

  return {
    title:
      typeof data.title === "string" &&
      data.title.trim()
        ? data.title.trim()
        : "ChatGPT Gespräch",

    model: model,
    shareId: shareId,

    updatedAt:
      typeof data.update_time === "number"
        ? data.update_time
        : null,

    messages: messages,
    stats: stats,
    warnings: []
  };
}

function flattenMessageContent(content, message) {
  const type =
    typeof content.content_type ===
    "string"
      ? content.content_type
      : "";

  const chunks = [];

  if (
    type === "text" ||
    (
      !type &&
      Array.isArray(content.parts)
    )
  ) {
    const parts =
      Array.isArray(content.parts)
        ? content.parts
        : [];

    for (const part of parts) {
      const value =
        extractTextPart(part);

      if (value) {
        chunks.push(value);
      }
    }
  } else if (type === "code") {
    const language =
      typeof content.language === "string" &&
      content.language !== "unknown"
        ? content.language
        : "";

    const code =
      typeof content.text === "string"
        ? content.text.replace(
            /\s+$/g,
            ""
          )
        : "";

    if (code) {
      chunks.push(
        "```" +
        language +
        "\n" +
        code +
        "\n```"
      );
    }
  } else if (
    type === "reasoning_recap"
  ) {
    const recap =
      typeof content.content === "string"
        ? content.content.trim()
        : "";

    if (recap) {
      chunks.push(
        "_" + recap + "_"
      );
    }
  } else if (type === "thoughts") {
    // Nur ausdrücklich sichtbare Zusammenfassungen.
    // Keine verborgenen Gedankengänge.

    const thoughts =
      Array.isArray(content.thoughts)
        ? content.thoughts
        : [];

    for (const thought of thoughts) {
      if (
        isObject(thought) &&
        typeof thought.summary ===
        "string" &&
        thought.summary.trim()
      ) {
        chunks.push(
          "_" +
          thought.summary.trim() +
          "_"
        );
      }
    }
  } else if (
    type === "multimodal_text"
  ) {
    const parts =
      Array.isArray(content.parts)
        ? content.parts
        : [];

    for (const part of parts) {
      if (typeof part === "string") {
        chunks.push(
          cleanExportText(part)
        );
        continue;
      }

      if (!isObject(part)) {
        continue;
      }

      const partType =
        String(
          part.content_type ||
          part.type ||
          ""
        );

      if (partType === "text") {
        const textValue = part.text;

        if (Array.isArray(textValue)) {
          for (const item of textValue) {
            if (
              typeof item === "string" &&
              item.trim()
            ) {
              chunks.push(
                cleanExportText(item)
              );
            }
          }
        } else if (
          typeof textValue === "string" &&
          textValue.trim()
        ) {
          chunks.push(
            cleanExportText(textValue)
          );
        }
      } else if (
        partType === "image_asset_pointer" ||
        partType === "file"
      ) {
        const pointer =
          typeof part.asset_pointer ===
          "string"
            ? part.asset_pointer
            : "";

        const label =
          partType ===
          "image_asset_pointer"
            ? "Bild aus dem Originalchat"
            : "Datei aus dem Originalchat";

        if (
          /^https?:\/\//i.test(pointer)
        ) {
          chunks.push(
            partType ===
            "image_asset_pointer"
              ? "![" +
                label +
                "](" +
                pointer +
                ")"
              : "[" +
                label +
                "](" +
                pointer +
                ")"
          );
        } else {
          chunks.push(
            "*[" +
            label +
            " – nicht direkt downloadbar]*"
          );
        }
      }
    }
  } else if (
    type === "tool_response"
  ) {
    if (
      CONFIG.INCLUDE_TOOL_MESSAGES &&
      typeof content.output === "string"
    ) {
      chunks.push(
        cleanExportText(
          content.output
        )
      );
    }
  } else if (
    typeof content.text === "string"
  ) {
    chunks.push(
      cleanExportText(
        content.text
      )
    );
  }

  const attachments =
    extractAttachmentMarkdown(
      message
    );

  if (attachments.length) {
    chunks.push(
      attachments.join("\n")
    );
  }

  return chunks
    .filter(Boolean)
    .join("\n\n")
    .trim();
}

function extractTextPart(part) {
  if (typeof part === "string") {
    const cleaned =
      cleanExportText(part);

    if (!cleaned) {
      return "";
    }

    const trimmed = cleaned.trim();

    if (
      trimmed.charAt(0) === "{" &&
      trimmed.charAt(
        trimmed.length - 1
      ) === "}"
    ) {
      try {
        const parsed =
          JSON.parse(trimmed);

        if (isObject(parsed)) {
          if (
            typeof parsed.response ===
            "string"
          ) {
            return cleanExportText(
              parsed.response
            );
          }

          if (
            typeof parsed.content ===
            "string"
          ) {
            return cleanExportText(
              parsed.content
            );
          }
        }
      } catch (_) {
        // Normalen Text übernehmen.
      }
    }

    return cleaned;
  }

  if (isObject(part)) {
    if (
      typeof part.text === "string"
    ) {
      return cleanExportText(
        part.text
      );
    }

    if (Array.isArray(part.text)) {
      return part.text
        .filter(function (item) {
          return (
            typeof item === "string"
          );
        })
        .map(cleanExportText)
        .filter(Boolean)
        .join("\n");
    }
  }

  return "";
}

function extractAttachmentMarkdown(message) {
  const metadata =
    isObject(message.metadata)
      ? message.metadata
      : {};

  const attachments =
    Array.isArray(metadata.attachments)
      ? metadata.attachments
      : [];

  const result = [];

  for (const attachment of attachments) {
    if (!isObject(attachment)) {
      continue;
    }

    const url =
      typeof attachment.download_url ===
      "string"
        ? attachment.download_url
        : (
            typeof attachment.file_url ===
            "string"
              ? attachment.file_url
              : ""
          );

    const name =
      typeof attachment.name ===
      "string" &&
      attachment.name.trim()
        ? attachment.name.trim()
        : "Anhang";

    const mime =
      typeof attachment.mime_type ===
      "string"
        ? attachment.mime_type
        : "";

    if (/^https?:\/\//i.test(url)) {
      result.push(
        /^image\//i.test(mime)
          ? "![" +
            escapeMarkdownLabel(name) +
            "](" +
            url +
            ")"
          : "[" +
            escapeMarkdownLabel(name) +
            "](" +
            url +
            ")"
      );
    } else {
      result.push(
        "*[Anhang: " +
        escapeMarkdownLabel(name) +
        " – nicht direkt downloadbar]*"
      );
    }
  }

  return result;
}

function cleanExportText(text) {
  let output = String(text || "")
    .replace(
      /[\uE000-\uF8FF]/g,
      ""
    )
    .replace(
      /\u0000/g,
      ""
    );

  if (
    CONFIG.REMOVE_CHATGPT_CITATION_MARKERS
  ) {
    output = output.replace(
      /(?:cite|filecite|navlist|filenavlist)[^]*/g,
      ""
    );
  }

  return output
    .replace(
      /[ \t]+\n/g,
      "\n"
    )
    .replace(
      /\n{4,}/g,
      "\n\n\n"
    )
    .trim();
}

function authorNameForRole(role) {
  if (role === "user") {
    return "Benutzer";
  }

  if (role === "tool") {
    return "Tool";
  }

  return "ChatGPT";
}

function hasUnclosedCodeFence(text) {
  const matches =
    String(text || "").match(/```/g);

  return Boolean(
    matches &&
    matches.length % 2 !== 0
  );
}

// -----------------------------------------------------------------------------
// DOM-Fallback
// -----------------------------------------------------------------------------

async function extractRenderedConversationWithWebView(url) {
  const webView = new WebView();

  await webView.loadRequest(
    makeBrowserLikeRequest(url)
  );

  await waitForRenderedMessages(webView);

  const result =
    await webView.evaluateJavaScript(`
      (() => {
        const items = [];
        const seen = new Set();

        const nodes = Array.from(
          document.querySelectorAll(
            '[data-message-author-role]'
          )
        );

        for (const node of nodes) {
          const role = node.getAttribute(
            'data-message-author-role'
          );

          if (
            role !== 'user' &&
            role !== 'assistant'
          ) {
            continue;
          }

          const container =
            node.closest('article') ||
            node;

          const key =
            container.getAttribute(
              'data-testid'
            ) ||
            role +
              ':' +
              (
                container.innerText ||
                ''
              ).slice(0, 200);

          if (seen.has(key)) {
            continue;
          }

          seen.add(key);

          const body =
            container.querySelector(
              '.markdown'
            ) ||
            container.querySelector(
              '[class*="markdown"]'
            ) ||
            node;

          const text = String(
            body.innerText ||
            body.textContent ||
            ''
          )
            .replace(
              /\\n{3,}/g,
              '\\n\\n'
            )
            .trim();

          if (text) {
            items.push({
              role: role,
              author:
                role === 'user'
                  ? 'Benutzer'
                  : 'ChatGPT',
              text: text,
              createdAt: null
            });
          }
        }

        const meta =
          document.querySelector(
            'meta[property="og:title"]'
          );

        const rawTitle =
          (
            meta &&
            meta.content
          ) ||
          document.title ||
          'ChatGPT Gespräch';

        const title =
          rawTitle
            .replace(
              /^ChatGPT\\s*[-–—:]\\s*/i,
              ''
            )
            .trim();

        return {
          title:
            title ||
            'ChatGPT Gespräch',
          model: '',
          shareId:
            location.pathname
              .split('/')
              .filter(Boolean)
              .pop() ||
            'shared',
          updatedAt: null,
          messages: items
        };
      })();
    `, false);

  if (
    !result ||
    !Array.isArray(result.messages) ||
    result.messages.length === 0
  ) {
    throw new Error(
      "Auch der Browser-Fallback konnte keine Nachrichten auslesen."
    );
  }

  result.parser = "dom-fallback";
  result.parserDetails =
    "Gerenderte sichtbare DOM-Nachrichten";

  result.stats = {
    sourceEntries:
      result.messages.length,
    exported:
      result.messages.length,
    skippedHidden: 0,
    skippedRole: 0,
    skippedRecipient: 0,
    skippedEmpty: 0,
    skippedDuplicate: 0,
    possiblyIncomplete: 0
  };

  result.warnings = [];

  return result;
}

async function waitForRenderedMessages(webView) {
  const attempts = Math.max(
    1,
    Number(
      CONFIG.DOM_RENDER_WAIT_ATTEMPTS
    ) || 1
  );

  for (
    let attempt = 1;
    attempt <= attempts;
    attempt++
  ) {
    const count =
      await webView.evaluateJavaScript(`
        document.querySelectorAll(
          '[data-message-author-role="user"],' +
          '[data-message-author-role="assistant"]'
        ).length
      `, false);

    if (Number(count) > 0) {
      return Number(count);
    }

    await sleep(
      CONFIG.DOM_RENDER_WAIT_MS
    );
  }

  throw new Error(
    "Die Share-Seite wurde geladen, aber die Nachrichten wurden nicht rechtzeitig gerendert."
  );
}

// -----------------------------------------------------------------------------
// Markdown erzeugen
// -----------------------------------------------------------------------------

function finalizeChatStats(chat) {
  if (!isObject(chat.stats)) {
    chat.stats = {
      sourceEntries:
        Array.isArray(chat.messages)
          ? chat.messages.length
          : 0,
      exported:
        Array.isArray(chat.messages)
          ? chat.messages.length
          : 0,
      skippedHidden: 0,
      skippedRole: 0,
      skippedRecipient: 0,
      skippedEmpty: 0,
      skippedDuplicate: 0,
      possiblyIncomplete: 0
    };
  }

  chat.stats.exported =
    chat.messages.length;

  if (!Array.isArray(chat.warnings)) {
    chat.warnings = [];
  }

  if (
    chat.stats.possiblyIncomplete > 0
  ) {
    chat.warnings.push(
      chat.stats.possiblyIncomplete +
      " Nachricht(en) könnten unvollständig sein."
    );
  }
}

function buildMarkdown(chat, sourceUrl) {
  const lines = [];

  lines.push(
    "# " +
    sanitizeHeading(
      chat.title ||
      "ChatGPT Gespräch"
    )
  );

  lines.push("");

  lines.push(
    "- **Quelle:** " +
    sourceUrl
  );

  lines.push(
    "- **Exportiert:** " +
    formatLocalDate(
      new Date()
    )
  );

  if (chat.model) {
    lines.push(
      "- **Modell:** " +
      chat.model
    );
  }

  if (chat.updatedAt) {
    lines.push(
      "- **Chat aktualisiert:** " +
      formatUnixTimestamp(
        chat.updatedAt
      )
    );
  }

  lines.push(
    "- **Nachrichten:** " +
    chat.messages.length
  );

  if (chat.parser) {
    lines.push(
      "- **Parser:** " +
      chat.parser
    );
  }

  if (chat.parserDetails) {
    lines.push(
      "- **Parser-Details:** " +
      chat.parserDetails
    );
  }

  if (
    Array.isArray(chat.warnings) &&
    chat.warnings.length > 0
  ) {
    for (const warning of chat.warnings) {
      lines.push(
        "- **Warnung:** " +
        warning
      );
    }
  }

  lines.push("");
  lines.push("---");
  lines.push("");

  for (
    let i = 0;
    i < chat.messages.length;
    i++
  ) {
    const message =
      chat.messages[i];

    lines.push(
      "## " +
      message.author
    );

    if (
      CONFIG.INCLUDE_MESSAGE_TIMESTAMPS &&
      message.createdAt
    ) {
      lines.push("");

      lines.push(
        "_" +
        formatUnixTimestamp(
          message.createdAt
        ) +
        "_"
      );
    }

    lines.push("");
    lines.push(
      message.text.trim()
    );
    lines.push("");

    if (
      i <
      chat.messages.length - 1
    ) {
      lines.push("---");
      lines.push("");
    }
  }

  if (
    CONFIG.INCLUDE_EXPORT_INTEGRITY_SECTION
  ) {
    appendIntegritySection(
      lines,
      chat
    );
  }

  return (
    lines
      .join("\n")
      .replace(
        /\n{4,}/g,
        "\n\n\n"
      )
      .trim() +
    "\n"
  );
}

function appendIntegritySection(lines, chat) {
  const stats =
    isObject(chat.stats)
      ? chat.stats
      : {};

  const skipped =
    Number(stats.skippedHidden || 0) +
    Number(stats.skippedRole || 0) +
    Number(stats.skippedRecipient || 0) +
    Number(stats.skippedEmpty || 0);

  const status =
    Number(stats.possiblyIncomplete || 0) === 0
      ? "PASS"
      : "WATCH";

  lines.push("");
  lines.push("---");
  lines.push("");
  lines.push("## Export-Integrität");
  lines.push("");
  lines.push(
    "- **Quellsequenz:** " +
    Number(stats.sourceEntries || 0)
  );
  lines.push(
    "- **Exportiert:** " +
    Number(stats.exported || 0)
  );
  lines.push(
    "- **Übersprungen:** " +
    skipped
  );
  lines.push(
    "- **Versteckt:** " +
    Number(stats.skippedHidden || 0)
  );
  lines.push(
    "- **Rollenfilter:** " +
    Number(stats.skippedRole || 0)
  );
  lines.push(
    "- **Empfängerfilter:** " +
    Number(stats.skippedRecipient || 0)
  );
  lines.push(
    "- **Leer/ungültig:** " +
    Number(stats.skippedEmpty || 0)
  );
  lines.push(
    "- **Duplikate:** " +
    Number(stats.skippedDuplicate || 0)
  );
  lines.push(
    "- **Möglicherweise unvollständig:** " +
    Number(stats.possiblyIncomplete || 0)
  );
  lines.push(
    "- **Parser:** " +
    (chat.parser || "unbekannt")
  );
  lines.push(
    "- **Status:** " +
    status
  );
  lines.push("");
  lines.push(
    "=== EXPORT COMPLETE ==="
  );
}

// -----------------------------------------------------------------------------
// Datei speichern
// -----------------------------------------------------------------------------

function saveMarkdownFile(chat, markdown) {
  const fm =
    FileManager.iCloud();

  const outputDirectory =
    fm.joinPath(
      fm.documentsDirectory(),
      CONFIG.OUTPUT_FOLDER
    );

  if (
    !fm.fileExists(
      outputDirectory
    )
  ) {
    fm.createDirectory(
      outputDirectory,
      true
    );
  }

  const stamp =
    fileDateStamp(
      new Date()
    );

  const suffix =
    chat.shareId
      ? "_" +
        String(
          chat.shareId
        ).slice(0, 8)
      : "";

  const base =
    sanitizeFileName(
      chat.title ||
      "ChatGPT_Gespraech"
    );

  let fileName =
    base +
    "_" +
    stamp +
    suffix +
    ".md";

  let filePath =
    fm.joinPath(
      outputDirectory,
      fileName
    );

  let counter = 2;

  while (
    fm.fileExists(filePath)
  ) {
    fileName =
      base +
      "_" +
      stamp +
      suffix +
      "_" +
      counter +
      ".md";

    filePath =
      fm.joinPath(
        outputDirectory,
        fileName
      );

    counter++;
  }

  fm.writeString(
    filePath,
    markdown
  );

  if (!fm.fileExists(filePath)) {
    throw new Error(
      "Die Markdown-Datei wurde nach dem Schreiben nicht gefunden."
    );
  }

  const savedContent =
    fm.readString(filePath);

  if (
    typeof savedContent !== "string"
  ) {
    throw new Error(
      "Die gespeicherte Markdown-Datei konnte nicht zurückgelesen werden."
    );
  }

  if (
    savedContent.length !==
    markdown.length
  ) {
    throw new Error(
      "Die gespeicherte Datei besitzt eine abweichende Länge. " +
      "Erwartet: " +
      markdown.length +
      ", gelesen: " +
      savedContent.length +
      "."
    );
  }

  const expectedEnd =
    markdown.slice(-300);

  const actualEnd =
    savedContent.slice(-300);

  if (expectedEnd !== actualEnd) {
    throw new Error(
      "Das Dateiende wurde nicht vollständig gespeichert."
    );
  }

  return {
    filePath: filePath,
    characterCount:
      savedContent.length
  };
}

// -----------------------------------------------------------------------------
// Erfolg und Fehler
// -----------------------------------------------------------------------------

async function showSuccess(
  filePath,
  messageCount,
  chat
) {
  const fm =
    FileManager.iCloud();

  const alert =
    new Alert();

  const status =
    chat &&
    chat.stats &&
    Number(
      chat.stats.possiblyIncomplete || 0
    ) > 0
      ? "WATCH"
      : "PASS";

  alert.title =
    "Markdown gespeichert";

  alert.message =
    messageCount +
    " Nachrichten wurden exportiert.\n" +
    "Parser: " +
    (chat.parser || "unbekannt") +
    "\n" +
    "Integrität: " +
    status +
    "\n\n" +
    "iCloud Drive/Scriptable/" +
    CONFIG.OUTPUT_FOLDER +
    "/\n" +
    fm.fileName(
      filePath,
      true
    );

  alert.addAction("Fertig");
  alert.addAction(
    "Datei teilen"
  );

  const choice =
    await alert.presentAlert();

  if (choice === 1) {
    await ShareSheet.present(
      [filePath]
    );
  }
}

async function showError(error) {
  const message =
    error && error.message
      ? error.message
      : String(
          error ||
          "Unbekannter Fehler"
        );

  console.error(message);

  const alert =
    new Alert();

  alert.title =
    "Chat-Export fehlgeschlagen";

  alert.message =
    message;

  alert.addAction("OK");

  await alert.presentAlert();
}

// -----------------------------------------------------------------------------
// Hilfsfunktionen
// -----------------------------------------------------------------------------

function sleep(milliseconds) {
  return new Promise(resolve => {
    Timer.schedule(
      Math.max(
        0,
        Number(milliseconds) || 0
      ) / 1000,
      false,
      resolve
    );
  });
}

function isObject(value) {
  return (
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value)
  );
}

function extractShareId(url) {
  const match =
    String(url || "").match(
      /\/(?:share|s)\/([^/?#]+)/i
    );

  return match
    ? match[1]
    : "";
}

function sanitizeHeading(value) {
  return String(value || "")
    .replace(
      /[\r\n]+/g,
      " "
    )
    .replace(
      /\s{2,}/g,
      " "
    )
    .trim();
}

function sanitizeFileName(value) {
  let name =
    String(
      value ||
      "ChatGPT_Gespraech"
    )
      .normalize("NFKC")
      .replace(
        /[\\/:*?"<>|]/g,
        "-"
      )
      .replace(
        /[\r\n\t]+/g,
        " "
      )
      .replace(
        /\s+/g,
        "_"
      )
      .replace(
        /_+/g,
        "_"
      )
      .replace(
        /^[-_. ]+|[-_. ]+$/g,
        ""
      )
      .slice(0, 80);

  return (
    name ||
    "ChatGPT_Gespraech"
  );
}

function escapeMarkdownLabel(value) {
  return String(value || "")
    .replace(
      /[\[\]]/g,
      "\\$&"
    );
}

function fileDateStamp(date) {
  const pad = number =>
    String(number).padStart(
      2,
      "0"
    );

  return (
    date.getFullYear() +
    "-" +
    pad(
      date.getMonth() + 1
    ) +
    "-" +
    pad(
      date.getDate()
    ) +
    "_" +
    pad(
      date.getHours()
    ) +
    "-" +
    pad(
      date.getMinutes()
    ) +
    "-" +
    pad(
      date.getSeconds()
    )
  );
}

function formatLocalDate(date) {
  try {
    return date.toLocaleString(
      "de-DE"
    );
  } catch (_) {
    return date.toISOString();
  }
}

function formatUnixTimestamp(timestamp) {
  const milliseconds =
    timestamp >
    100000000000
      ? timestamp
      : timestamp * 1000;

  return formatLocalDate(
    new Date(milliseconds)
  );
}