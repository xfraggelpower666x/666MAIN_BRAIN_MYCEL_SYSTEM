const APP = {
  name: '666 ChatBackup Scriptable iPhone',
  version: '1.0.9',
  schema: '666.chatbackup.machine.v1',
  schemaVersion: '1.3.0',
  structureSchema: '666.chatbackup.structure-inspector.v1',
  structureSchemaVersion: '1.1.0'
};

const CONFIG = {
  OUTPUT_FOLDER: '666_CHATBACKUP_SCRIPTABLE',
  SETTINGS_FILE: 'settings.json',
  INCLUDE_TOOL_MESSAGES: false,
  INCLUDE_MESSAGE_TIMESTAMPS: false,
  REMOVE_CHATGPT_CITATION_MARKERS: true,
  REQUEST_TIMEOUT_SECONDS: 60,
  DOWNLOAD_RETRIES: 3,
  MAX_RAW_HTML_CHARS: 12000000,
  DEFAULT_LANGUAGE: 'en'
};

const fm = FileManager.iCloud();
const rootDir = fm.joinPath(fm.documentsDirectory(), CONFIG.OUTPUT_FOLDER);
if (!fm.fileExists(rootDir)) fm.createDirectory(rootDir, true);
const settingsPath = fm.joinPath(rootDir, CONFIG.SETTINGS_FILE);
let settings = loadSettings();
let currentChat = null;
let currentSourceHtml = null;
let lastSaved = [];

await mainMenu();
Script.complete();

async function mainMenu() {
  while (true) {
    const a = new Alert();
    a.title = `${APP.name} v${APP.version}`;
    a.message = t(
      'Guided iPhone workflow for public shares, private/manual transcripts, group chats, structured JSON and image downloads.',
      'Geführter iPhone-Workflow für öffentliche Shares, private/manuelle Verläufe, Gruppenchats, Struktur-JSON und Bilddownloads.'
    );
    a.addAction(t('Public Share Link', 'Öffentlicher Share-Link'));
    a.addAction(t('Private / Manual Import', 'Privat / Manuell importieren'));
    a.addAction(t('Current Chat / Structure', 'Aktueller Chat / Struktur'));
    a.addAction(t('Chat Images', 'Chat-Bilder'));
    a.addAction(t('Export', 'Exportieren'));
    a.addAction(t('Language', 'Sprache'));
    a.addAction(t('Diagnostics / Self-Test', 'Diagnose / Selbsttest'));
    a.addAction(t('Help', 'Hilfe'));
    a.addCancelAction(t('Close', 'Schließen'));
    const i = await a.presentSheet();
    if (i < 0) return;
    if (i === 0) await guidedPublicShare();
    if (i === 1) await guidedManualImport();
    if (i === 2) await showCurrentStructure();
    if (i === 3) await imageMenu();
    if (i === 4) await exportMenu();
    if (i === 5) await languageMenu();
    if (i === 6) await diagnosticsMenu();
    if (i === 7) await helpMenu();
  }
}

function t(en, de) { return settings.language === 'de' ? de : en; }

function loadSettings() {
  const fallback = { language: CONFIG.DEFAULT_LANGUAGE, autoSaveRawSource: true, saveImages: true };
  try {
    if (!fm.fileExists(settingsPath)) return fallback;
    const parsed = JSON.parse(fm.readString(settingsPath));
    return Object.assign({}, fallback, parsed || {});
  } catch (_) { return fallback; }
}
function saveSettings() {
  fm.writeString(settingsPath, JSON.stringify(settings, null, 2));
}

async function languageMenu() {
  const a = new Alert();
  a.title = t('Language', 'Sprache');
  a.message = t('English is the default on first start. The selected language is saved for the next system start.', 'Englisch ist beim ersten Start Standard. Die gewählte Sprache wird für den nächsten Systemstart gespeichert.');
  a.addAction('English');
  a.addAction('Deutsch');
  a.addCancelAction(t('Cancel', 'Abbrechen'));
  const i = await a.presentSheet();
  if (i === 0) settings.language = 'en';
  if (i === 1) settings.language = 'de';
  if (i === 0 || i === 1) { saveSettings(); await info(t('Language saved.', 'Sprache gespeichert.')); }
}

async function diagnosticsMenu() {
  const a = new Alert();
  a.title = t('Diagnostics / Self-Test', 'Diagnose / Selbsttest');
  a.message = t(
    'Run a local parser/file-system self-test or probe one public share without creating a chat backup.',
    'Führe einen lokalen Parser-/Dateisystem-Selbsttest aus oder prüfe einen öffentlichen Share ohne Chat-Backup zu erzeugen.'
  );
  a.addAction(t('Run offline self-test', 'Offline-Selbsttest starten'));
  a.addAction(t('Probe public share', 'Öffentlichen Share prüfen'));
  a.addAction(t('Run host acceptance', 'Host-Abnahme starten'));
  if (currentSourceHtml) a.addAction(t('Copy current source fingerprint', 'Aktuellen Source-Fingerprint kopieren'));
  a.addCancelAction(t('Back', 'Zurück'));
  const choice = await a.presentSheet();
  if (choice < 0) return;
  if (choice === 0) await runOfflineSelfTest();
  else if (choice === 1) await runShareCompatibilityProbe();
  else if (choice === 2) await runHostAcceptance();
  else if (choice === 3 && currentSourceHtml) {
    Pasteboard.copyString(JSON.stringify(sourceFingerprint(currentSourceHtml), null, 2));
    await info(t('Source fingerprint copied.', 'Source-Fingerprint kopiert.'));
  }
}

async function runOfflineSelfTest() {
  const checks = [];
  const add = (name, ok, detail='') => checks.push({name, status:ok ? 'PASS' : 'FAIL', detail:String(detail || '')});
  try {
    const fixtureLoader = [
      {}, 'loaderData', {'_3':4}, 'routes/share.$shareId.($action)', {'_5':6,'_7':8},
      'sharedConversationId', 'fixture-share', 'serverResponse', {'_9':10}, 'data',
      {title:'Flight Fixture', mapping:{m1:{message:{id:'m1',author:{role:'assistant',name:'ChatGPT'},content:{content_type:'text',parts:['Hello Flight']},metadata:{},recipient:'all',status:'finished_successfully'}}}, linear_conversation:[{id:'m1'}]}
    ];
    const flightHtml = '<script>window.__reactRouterContext.streamController.enqueue(' + JSON.stringify(JSON.stringify(fixtureLoader)) + ');</script>';
    const flight = parseConversation(flightHtml, 'https://chatgpt.com/share/fixture-share');
    add('REACT_FLIGHT_FIXTURE', flight.parser === 'react-flight' && flight.messages.length === 1 && /Hello Flight/.test(flight.messages[0].text), `${flight.parser}/${flight.messages.length}`);
  } catch (e) { add('REACT_FLIGHT_FIXTURE', false, e && e.message || e); }

  try {
    const ssrHtml = '<html><head><title>SSR &amp; Fixture</title></head><body><ol data-conversation-transcript>' +
      '<li data-message-role="assistant" id="a1"><div data-assistant-markdown-root><p>Hello SSR</p><img src="https://example.com/image.png"></div></li>' +
      '<li data-message-role="user" id="u1"><p data-user-message-copy>Hi User</p></li>' +
      '</ol></body></html>';
    const ssr = parseConversation(ssrHtml, 'https://chatgpt.com/share/fixture-ssr');
    const imgCount = (ssr.messages || []).reduce((n,m)=>n + ((m.assets || []).length), 0);
    const human = (ssr.messages || []).find(m=>m.role === 'user');
    add('SSR_SOURCE_FIXTURE', ssr.parser === 'ssr-source-transcript' && ssr.messages.length === 2, `${ssr.parser}/${ssr.messages.length}`);
    add('SSR_HTTP_IMAGE_FIXTURE', imgCount === 1, `assets=${imgCount}`);
    add('FAIL_CLOSED_USER_IDENTITY', Boolean(human && human.participantResolution === 'UNRESOLVED'), human ? human.participantResolution : 'missing');
  } catch (e) {
    add('SSR_SOURCE_FIXTURE', false, e && e.message || e);
    add('SSR_HTTP_IMAGE_FIXTURE', false, 'fixture failed');
    add('FAIL_CLOSED_USER_IDENTITY', false, 'fixture failed');
  }

  try {
    const manual = parseManualTranscript('You said:\nHello\n\nChatGPT said:\nHi');
    add('MANUAL_TRANSCRIPT_FIXTURE', manual.messages.length === 2 && manual.messages[0].role === 'user' && manual.messages[1].role === 'assistant', `messages=${manual.messages.length}`);
  } catch (e) { add('MANUAL_TRANSCRIPT_FIXTURE', false, e && e.message || e); }

  try {
    const fp = sourceFingerprint('<ol data-conversation-transcript><li data-message-role="assistant"><div data-assistant-markdown-root>x</div></li></ol>');
    add('SOURCE_FINGERPRINT_FIXTURE', fp.ssrTranscriptRoots === 1 && fp.ssrRoleMarkers === 1 && fp.assistantMarkdownRoots === 1, JSON.stringify(fp));
  } catch (e) { add('SOURCE_FINGERPRINT_FIXTURE', false, e && e.message || e); }

  try {
    const probePath = fm.joinPath(rootDir, 'selftest_io_probe.txt');
    const content = '666_CHATBACKUP_SELFTEST_' + APP.version + '_' + new Date().toISOString();
    fm.writeString(probePath, content);
    await verifyText(probePath, content);
    const readback = fm.readString(probePath);
    add('SCRIPTABLE_FILE_WRITE_READBACK', readback === content, `FileManager.iCloud chars=${readback.length}`);
    try { fm.remove(probePath); } catch (_) {}
  } catch (e) { add('SCRIPTABLE_FILE_WRITE_READBACK', false, e && e.message || e); }

  const passed = checks.filter(x=>x.status==='PASS').length;
  const failed = checks.length - passed;
  const report = {status:failed ? 'SELFTEST_FAIL' : 'SELFTEST_PASS', tool:APP.name, version:APP.version, executedAt:new Date().toISOString(), checks, passed, failed, scriptableRuntime:typeof Script !== 'undefined' && typeof WebView !== 'undefined' && typeof FileManager !== 'undefined'};
  const dir = fm.joinPath(rootDir, 'selftest');
  if (!fm.fileExists(dir)) fm.createDirectory(dir, true);
  const path = fm.joinPath(dir, 'selftest_' + dateStamp(new Date()) + '.json');
  const json = JSON.stringify(report, null, 2);
  fm.writeString(path, json);
  await verifyText(path, json);
  Pasteboard.copyString(json);
  const a = new Alert();
  a.title = report.status;
  a.message = `${passed}/${checks.length} PASS\n\n` + checks.map(x=>`${x.status === 'PASS' ? '✓' : '✗'} ${x.name}${x.detail ? ' — ' + x.detail : ''}`).join('\n');
  a.addAction(t('OK — report copied', 'OK — Bericht kopiert'));
  a.addAction(t('Share report file', 'Berichtsdatei teilen'));
  const choice = await a.presentAlert();
  if (choice === 1) await ShareSheet.present([path]);
}

async function runShareCompatibilityProbe() {
  const url = await resolveShareUrl();
  if (!url) return;
  const normalized = normalizeChatGptUrl(url);
  if (/\/c\//i.test(normalized) || !/\/(?:share|s)\//i.test(normalized)) {
    await info(t('A public /share/ or /s/ link is required.', 'Ein öffentlicher /share/- oder /s/-Link ist erforderlich.'));
    return;
  }
  await progressInfo(t('Running compatibility probe…', 'Kompatibilitätsprüfung läuft…'));
  const report = {status:'PROBE_STARTED', tool:APP.name, version:APP.version, sourceUrl:normalized, executedAt:new Date().toISOString(), sourceMarkers:null, parser:null, messageCount:0, participantCount:0, imageAssetCount:0, error:null};
  let html = null;
  try {
    html = await fetchWithRetry(normalized);
    report.sourceMarkers = sourceFingerprint(html);
    const chat = parseConversation(html, normalized);
    finalizeChat(chat);
    report.status = 'PROBE_PASS';
    report.parser = chat.parser || null;
    report.parserDetails = chat.parserDetails || null;
    report.messageCount = (chat.messages || []).length;
    report.participantCount = (chat.participants || []).length;
    report.imageAssetCount = (chat.messages || []).reduce((n,m)=>n + ((m.assets || []).length),0);
    report.warnings = chat.warnings || [];
  } catch (e) {
    report.status = 'PROBE_FAIL';
    report.error = String(e && e.message || e);
    if (!report.sourceMarkers) report.sourceMarkers = sourceFingerprint(html);
  }
  const dir = fm.joinPath(rootDir, 'diagnostics');
  if (!fm.fileExists(dir)) fm.createDirectory(dir, true);
  const path = fm.joinPath(dir, 'share_probe_' + dateStamp(new Date()) + '.json');
  const json = JSON.stringify(report, null, 2);
  fm.writeString(path, json);
  await verifyText(path, json);
  Pasteboard.copyString(json);
  const a = new Alert();
  a.title = report.status;
  a.message = report.status === 'PROBE_PASS'
    ? `${report.parser}\n${report.messageCount} message(s)\n${report.imageAssetCount} image asset(s)\n\n` + t('No backup was created. Report copied.', 'Kein Backup erzeugt. Bericht kopiert.')
    : `${report.error}\n\n` + t('No backup was created. Diagnostic report copied.', 'Kein Backup erzeugt. Diagnosebericht kopiert.');
  a.addAction(t('OK', 'OK'));
  a.addAction(t('Share report file', 'Berichtsdatei teilen'));
  const choice = await a.presentAlert();
  if (choice === 1) await ShareSheet.present([path]);
}


async function runHostAcceptance() {
  const url = await resolveShareUrl();
  if (!url) return;
  const normalized = normalizeChatGptUrl(url);
  if (/\/c\//i.test(normalized) || !/\/(?:share|s)\//i.test(normalized)) {
    await info(t('A public /share/ or /s/ link is required.', 'Ein öffentlicher /share/- oder /s/-Link ist erforderlich.'));
    return;
  }

  await progressInfo(t('Running full host acceptance…', 'Vollständige Host-Abnahme läuft…'));
  const checks = [];
  const add = (name, ok, detail='') => checks.push({name, status:ok ? 'PASS' : 'FAIL', detail:String(detail || '')});
  const receipt = {
    schema:'666.chatbackup.host-acceptance.v1',
    status:'HOST_ACCEPTANCE_STARTED',
    tool:APP.name,
    version:APP.version,
    sourceUrl:normalized,
    executedAt:new Date().toISOString(),
    parser:null,
    parserDetails:null,
    messageCount:0,
    participantCount:0,
    imageAssetCount:0,
    sourceMarkers:null,
    exportedFiles:[],
    checks
  };

  const dir = uniquePath(rootDir, 'host_acceptance_' + dateStamp(new Date()), '');
  if (!fm.fileExists(dir)) fm.createDirectory(dir, true);
  let html = null;
  try {
    const imported = await importPublicShare(normalized);
    html = imported.html;
    receipt.sourceMarkers = html ? sourceFingerprint(html) : null;
    receipt.importAttempts = imported.attempts;
    if (!imported.chat) throw new Error(imported.attempts.map(x => `${x.path}: ${x.error}`).join(' | '));
    const chat = imported.chat;
    receipt.importPath = imported.attempts[imported.attempts.length - 1].path;
    add('LIVE_SHARE_LOAD', true, receipt.importPath);
    receipt.parser = chat.parser || null;
    receipt.parserDetails = chat.parserDetails || null;
    receipt.messageCount = (chat.messages || []).length;
    receipt.participantCount = (chat.participants || []).length;
    receipt.imageAssetCount = (chat.messages || []).reduce((n,m)=>n + ((m.assets || []).length), 0);
    add('LIVE_SHARE_PARSE', receipt.messageCount > 0, `${receipt.parser}/${receipt.messageCount}`);
    add('PARSER_PROVENANCE', Boolean(receipt.parser), receipt.parser || 'missing');

    const artifacts = [
      ['chat.md', buildMarkdown(chat)],
      ['chat.json', JSON.stringify(machineExport(chat), null, 2)],
      ['chat.jsonl', buildJsonl(chat)],
      ['structure_inspector.json', JSON.stringify(structureSnapshot(chat), null, 2)],
      ['source_fingerprint.json', JSON.stringify(receipt.sourceMarkers, null, 2)]
    ];
    if (html && html.length <= CONFIG.MAX_RAW_HTML_CHARS) artifacts.push(['share-source.html', html]);

    for (const [name, data] of artifacts) {
      const path = fm.joinPath(dir, name);
      fm.writeString(path, data);
      await verifyText(path, data);
      const size = fm.fileSize(path);
      receipt.exportedFiles.push({name, size});
      add('EXPORT_READBACK_' + name.toUpperCase().replace(/[^A-Z0-9]+/g,'_'), size > 0, `bytes=${size}`);
    }

    const jsonPayload = JSON.parse(fm.readString(fm.joinPath(dir, 'chat.json')));
    const jsonMessages = jsonPayload && Array.isArray(jsonPayload.messages) ? jsonPayload.messages.length : -1;
    add('JSON_MESSAGE_COUNT_READBACK', jsonMessages === receipt.messageCount, `${jsonMessages}/${receipt.messageCount}`);

    const structurePayload = JSON.parse(fm.readString(fm.joinPath(dir, 'structure_inspector.json')));
    const structureMessages = structurePayload && Array.isArray(structurePayload.messages) ? structurePayload.messages.length : -1;
    add('STRUCTURE_MESSAGE_COUNT_READBACK', structureMessages === receipt.messageCount, `${structureMessages}/${receipt.messageCount}`);
  } catch (e) {
    receipt.error = String(e && e.message || e);
    add('HOST_ACCEPTANCE_PIPELINE', false, receipt.error);
  }

  const failed = checks.filter(x=>x.status !== 'PASS');
  receipt.status = failed.length ? 'HOST_ACCEPTANCE_FAIL' : 'HOST_ACCEPTANCE_PASS';
  receipt.passed = checks.length - failed.length;
  receipt.failed = failed.length;
  receipt.completedAt = new Date().toISOString();
  const receiptPath = fm.joinPath(dir, 'host_acceptance_receipt.json');
  const json = JSON.stringify(receipt, null, 2);
  fm.writeString(receiptPath, json);
  await verifyText(receiptPath, json);
  Pasteboard.copyString(json);

  const a = new Alert();
  a.title = receipt.status;
  a.message = `${receipt.passed}/${checks.length} PASS\n${receipt.messageCount} message(s)\n${receipt.parser || 'no parser'}\n\n` +
    t('Receipt copied. This closes the iPhone host gate only when status is HOST_ACCEPTANCE_PASS on the real iPhone.',
      'Receipt kopiert. Das iPhone-Host-Gate ist nur geschlossen, wenn auf dem echten iPhone HOST_ACCEPTANCE_PASS erreicht wird.');
  a.addAction(t('OK', 'OK'));
  a.addAction(t('Share acceptance folder files', 'Abnahmedateien teilen'));
  const choice = await a.presentAlert();
  if (choice === 1) {
    const paths = receipt.exportedFiles.map(x=>fm.joinPath(dir,x.name));
    paths.push(receiptPath);
    await ShareSheet.present(paths.slice(0,20));
  }
}

async function guidedPublicShare() {
  const url = await resolveShareUrl();
  if (!url) return;
  const normalized = normalizeChatGptUrl(url);
  if (/\/c\//i.test(normalized)) {
    await info(t('This is a private /c/ link. Use Private / Manual Import instead.', 'Das ist ein privater /c/-Link. Bitte Privat / Manuell importieren verwenden.'));
    return;
  }
  if (!/\/(?:share|s)\//i.test(normalized)) throw new Error(t('A public /share/ link is required.', 'Ein öffentlicher /share/-Link ist erforderlich.'));

  await progressInfo(t('Loading and analyzing public share…', 'Öffentlichen Share laden und analysieren…'));
  const imported = await importPublicShare(normalized);
  currentChat = imported.chat;
  currentSourceHtml = imported.html;
  if (!currentChat) {
    const [direct, ...fallbacks] = imported.attempts;
    await reportShareFailure(direct.error, fallbacks.map(x => `${x.path}: ${x.error}`).join(' | '), normalized, currentSourceHtml);
    return;
  }
  await showSummary(currentChat);
}

// Beide Menuepfade verwenden denselben Import und protokollieren den tatsaechlichen Weg.
async function importPublicShare(url) {
  let html = null;
  const attempts = [];
  const paths = [
    ['DIRECT_SOURCE', async () => {
      html = await fetchWithRetry(url);
      return parseConversation(html, url);
    }, ''],
    ['SOURCE_DOM', async () => {
      if (!html) throw new Error('NO_FETCHED_SOURCE');
      return extractViaFetchedHtml(html, url);
    }, t('Fetched-source DOM recovery used; dynamic UI bindings and attachments may be incomplete.', 'DOM-Wiederherstellung aus geladener Quelle verwendet; dynamische UI-Bindungen und Anhänge können unvollständig sein.')],
    ['LIVE_WEBVIEW', () => extractViaWebView(url),
      t('Live WebView DOM fallback used; dynamic UI bindings and attachments may be incomplete.', 'Live-WebView-DOM-Fallback verwendet; dynamische UI-Bindungen und Anhänge können unvollständig sein.')]
  ];
  for (const [path, load, warning] of paths) {
    try {
      const chat = await load();
      if (!chat.messages || !chat.messages.length) throw new Error('NO_MESSAGES');
      if (warning) chat.warnings.push(warning);
      chat.sourceUrl = url;
      chat.primaryError = attempts.length ? attempts[0].error : null;
      finalizeChat(chat);
      attempts.push({path, status:'PASS'});
      return {chat, html, attempts};
    } catch (error) {
      attempts.push({path, status:'FAIL', error:String(error && error.message || error)});
    }
  }
  return {chat:null, html, attempts};
}

function sourceFingerprint(html) {
  const src = String(html || '');
  const count = re => (src.match(re) || []).length;
  return {
    htmlCharacters: src.length,
    scriptTags: count(/<script\b/gi),
    reactFlightMarkers: count(/streamController\.enqueue\(|__next_f\.push\(/g),
    linearConversationMarkers: count(/linear_conversation/g),
    legacyRoleMarkers: count(/data-message-author-role/g),
    legacyTurnMarkers: count(/conversation-turn-/g),
    ssrTranscriptRoots: count(/data-conversation-transcript/g),
    ssrRoleMarkers: count(/data-message-role\s*=/g),
    assistantMarkdownRoots: count(/data-assistant-markdown-root/g),
    userMessageCopyMarkers: count(/data-user-message-copy/g)
  };
}

async function reportShareFailure(primary, fallback, url, html) {
  const details = {
    status: 'IMPORT_FAILED_NO_MESSAGES',
    tool: APP.name,
    version: APP.version,
    sourceUrl: url,
    primaryParserError: primary,
    webViewError: fallback,
    fetchedHtmlCharacters: html ? html.length : 0,
    sourceMarkers: sourceFingerprint(html),
    note: 'No messages extracted. No incomplete backup has been generated.'
  };
  console.warn(JSON.stringify(details, null, 2));
  const a = new Alert();
  a.title = t('Share could not be read', 'Share konnte nicht gelesen werden');
  a.message = t(
    'Neither structured data nor rendered messages were available. No empty backup was written. You can import a copied transcript manually or copy the diagnostic report.',
    'Weder strukturierte Daten noch gerenderte Nachrichten waren verfügbar. Es wurde kein leeres Backup geschrieben. Du kannst den kopierten Chat manuell importieren oder den Diagnosebericht kopieren.'
  ) + '\n\n' + fallback.slice(0, 350);
  a.addAction(t('Manual import', 'Manuell importieren'));
  a.addAction(t('Copy diagnosis', 'Diagnose kopieren'));
  a.addAction(t('Save source diagnostics', 'Quelldiagnose speichern'));
  a.addCancelAction(t('Back', 'Zurück'));
  const choice = await a.presentAlert();
  if (choice === 0) await guidedManualImport();
  if (choice === 1) Pasteboard.copyString(JSON.stringify(details, null, 2));
  if (choice === 2) await saveSourceDiagnostics(details, html);
}

async function saveSourceDiagnostics(details, html) {
  const caution = new Alert();
  caution.title = t('Source contains sensitive data', 'Quelle kann sensible Daten enthalten');
  caution.message = t(
    'The fetched HTML may contain the complete public share, names and message text. Save to your private iCloud Scriptable folder only. Review before sharing.',
    'Der HTML-Quelltext kann den gesamten öffentlichen Share, Namen und Nachrichtentexte enthalten. Speichere ihn nur im privaten Scriptable-iCloud-Ordner und prüfe ihn vor dem Teilen.'
  );
  caution.addAction(t('Save locally', 'Lokal speichern'));
  caution.addCancelAction(t('Cancel', 'Abbrechen'));
  if (await caution.presentAlert() !== 0) return;
  const dir = fm.joinPath(rootDir, 'diagnostic_' + dateStamp(new Date()));
  fm.createDirectory(dir, true);
  const report = Object.assign({}, details, {
    sourcePresent: typeof html === 'string' && html.length > 0,
    sourceMarkers: sourceFingerprint(html),
    nextDataMarkers: html ? (html.match(/__NEXT_DATA__/g) || []).length : 0,
    mappingMentions: html ? (html.match(/linear_conversation|\\"mapping\\"/g) || []).length : 0
  });
  const jsonPath = fm.joinPath(dir, 'diagnostic.json');
  const json = JSON.stringify(report, null, 2);
  fm.writeString(jsonPath, json);
  await verifyText(jsonPath, json);
  const saved = [jsonPath];
  if (html) {
    const htmlPath = fm.joinPath(dir, 'fetched_share_source.html');
    fm.writeString(htmlPath, html);
    await verifyText(htmlPath, html);
    saved.push(htmlPath);
  }
  await info(t('Source and diagnosis saved in private iCloud Scriptable folder. No chat export was created.',
    'Quelle und Diagnose im privaten Scriptable-iCloud-Ordner gespeichert. Kein Chat-Export erzeugt.'));
  await shareOrDone(saved);
}

async function resolveShareUrl() {
  const candidates = [];
  if (Array.isArray(args.urls)) candidates.push(...args.urls);
  if (Array.isArray(args.plainTexts)) candidates.push(...args.plainTexts);
  if (typeof args.shortcutParameter === 'string') candidates.push(args.shortcutParameter);
  const clip = Pasteboard.pasteString();
  if (clip) candidates.push(clip);
  for (const c of candidates) { const u = findChatGptUrl(String(c || '')); if (u) return u; }
  const a = new Alert();
  a.title = t('Public ChatGPT Share Link', 'Öffentlicher ChatGPT-Share-Link');
  a.message = t('Paste a public /share/ link. You can copy it in ChatGPT using Share → Copy link.', 'Füge einen öffentlichen /share/-Link ein. In ChatGPT: Teilen → Link kopieren.');
  a.addTextField('https://chatgpt.com/share/...', '');
  a.addAction(t('Load', 'Laden'));
  a.addCancelAction(t('Cancel', 'Abbrechen'));
  if (await a.presentAlert() < 0) return null;
  return findChatGptUrl(a.textFieldValue(0));
}

async function guidedManualImport() {
  const clip = String(Pasteboard.pasteString() || '');
  const a = new Alert();
  a.title = t('Private / Manual Import', 'Privat / Manuell importieren');
  a.message = t(
    `1. Open the private or full ChatGPT conversation.\n2. Copy the complete visible transcript.\n3. Return here and choose Analyze Clipboard.\n\nClipboard: ${clip.length.toLocaleString()} characters.`,
    `1. Öffne den privaten oder vollen ChatGPT-Chat.\n2. Kopiere den gesamten sichtbaren Verlauf.\n3. Kehre hierher zurück und wähle Zwischenablage analysieren.\n\nZwischenablage: ${clip.length.toLocaleString()} Zeichen.`
  );
  a.addAction(t('Analyze Clipboard', 'Zwischenablage analysieren'));
  a.addAction(t('How to Copy', 'So kopierst du den Chat'));
  a.addCancelAction(t('Cancel', 'Abbrechen'));
  const i = await a.presentSheet();
  if (i === 1) { await manualCopyHelp(); return; }
  if (i !== 0) return;
  if (!clip.trim()) { await info(t('Clipboard is empty.', 'Zwischenablage ist leer.')); return; }
  currentSourceHtml = null;
  currentChat = parseManualTranscript(clip);
  finalizeChat(currentChat);
  await showSummary(currentChat);
}

function parseManualTranscript(text) {
  const src = String(text || '').replace(/\r\n?/g, '\n').trim();
  const lines = src.split('\n');
  const markers = [
    {re:/^(?:You said|User|Benutzer|Du)\s*:\s*$/i, role:'user', name:null},
    {re:/^(?:ChatGPT said|ChatGPT|Assistant|Assistent)\s*:\s*$/i, role:'assistant', name:'ChatGPT'},
    {re:/^([A-Za-zÀ-ÿ0-9_. -]{1,60})\s*:\s*$/, role:'speaker', name:null}
  ];
  let inFence = false, current = null, messages = [], speakerNames = new Set();
  const flush = () => {
    if (!current) return;
    const body = current.body.join('\n').trim();
    if (!body) { current = null; return; }
    const id = `manual-${String(messages.length+1).padStart(4,'0')}`;
    const role = current.role === 'speaker' ? (current.name && /^chatgpt$/i.test(current.name) ? 'assistant' : 'user') : current.role;
    const author = current.name || (role === 'assistant' ? 'ChatGPT' : t('User','Benutzer'));
    messages.push(makeMessage({id, role, author, text: body, rawContent:{sourceText:body}, rawMetadata:{manual:true}, contentType:'manual_text', status:'manual', recipient:'all'}));
    current = null;
  };
  for (let idx=0; idx<lines.length; idx++) {
    const line = lines[idx];
    if (/^```/.test(line.trim())) { inFence = !inFence; if (current) current.body.push(line); continue; }
    if (!inFence) {
      let matched = null;
      for (const m of markers) {
        const mm = line.trim().match(m.re);
        if (mm) { matched = {role:m.role, name:m.name || (m.role==='speaker' ? mm[1].trim() : null)}; break; }
      }
      if (matched) {
        if (matched.role === 'speaker' && /^(Introduction|Summary|Details|Notes|Result|Results|Help|Hilfe)$/i.test(matched.name || '')) {
          if (current) current.body.push(line);
          continue;
        }
        flush();
        current = {role:matched.role, name:matched.name, body:[]};
        if (matched.name && matched.role === 'speaker') speakerNames.add(matched.name.toLowerCase());
        continue;
      }
    }
    if (!current) current = {role:'user', name:null, body:[]};
    current.body.push(line);
  }
  flush();
  if (!messages.length) messages = [makeMessage({id:'manual-0001', role:'user', author:t('User','Benutzer'), text:src, rawContent:{sourceText:src}, rawMetadata:{manual:true, unresolvedTurns:true}, contentType:'manual_text', status:'manual', recipient:'all'})];
  const participants = buildParticipants(messages);
  const humanCount = participants.filter(p => p.kind === 'human' && p.resolution !== 'UNRESOLVED').length;
  return {
    title: t('Manual Chat Import', 'Manueller Chat-Import'),
    shareId: 'manual', sourceUrl: '', parser:'manual-transcript', parserDetails:'Clipboard transcript analysis', updatedAt:null,
    messages, participants, participantCount:participants.length, isGroupChat:humanCount >= 2, conversationType:humanCount >= 2 ? 'group' : 'direct',
    stats:{sourceEntries:messages.length, exported:messages.length, skippedHidden:0, skippedRole:0, skippedRecipient:0, skippedEmpty:0, skippedDuplicate:0, possiblyIncomplete:0},
    warnings:[]
  };
}

function makeMessage(o) {
  const copy = extractCopyFields(String(o.text || ''));
  return {
    id:o.id || '', role:o.role || 'assistant', author:o.author || 'ChatGPT', recipient:o.recipient || 'all', status:o.status || '',
    createdAt:o.createdAt || null, contentType:o.contentType || '', renderedText:renderMarkdownText(o.text || ''), text:renderMarkdownText(o.text || ''),
    rawContent:o.rawContent || {}, rawMetadata:o.rawMetadata || {}, copyFields:copy.fields, warnings:copy.warnings, assets:o.assets || [],
    participantId:o.participantId || '', participantDisplayName:o.participantDisplayName || o.author || '', participantKind:o.participantKind || (o.role==='assistant'?'assistant':'human'),
    participantUsername:o.participantUsername || '', participantResolution:o.participantResolution || (o.author ? 'SOURCE_LABEL' : 'UNRESOLVED')
  };
}

function buildParticipants(messages) {
  const byId = new Map();
  const byName = new Map();
  for (const m of messages) {
    const name = String(m.participantDisplayName || m.author || '').trim();
    const kind = m.participantKind || (m.role === 'assistant' ? 'assistant' : 'human');
    let id = String(m.participantId || '').trim();
    if (!id && name) id = `name:${name.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}`;
    if (!id) id = `unresolved:${m.role}`;
    const p = {participantId:id, displayName:name || (kind==='assistant'?'ChatGPT':t('Unknown','Unbekannt')), kind, username:m.participantUsername || '', resolution:m.participantResolution || (name?'SOURCE_LABEL':'UNRESOLVED')};
    if (!byId.has(id)) byId.set(id,p);
    if (name && !byName.has(name.toLowerCase())) byName.set(name.toLowerCase(), p);
    m.participantId = id; m.participantDisplayName = p.displayName; m.participantKind = kind; m.participantResolution = p.resolution;
  }
  return Array.from(byId.values());
}

function finalizeChat(chat) {
  if (!chat.participants) chat.participants = buildParticipants(chat.messages || []);
  chat.participantCount = chat.participants.length;
  const humans = chat.participants.filter(p => p.kind === 'human' && p.resolution !== 'UNRESOLVED');
  chat.isGroupChat = Boolean(chat.isGroupChat || humans.length >= 2);
  chat.conversationType = chat.isGroupChat ? 'group' : (chat.conversationType || 'direct');
  chat.stats = chat.stats || {};
  chat.stats.exported = (chat.messages || []).length;
  chat.warnings = chat.warnings || [];
  chat.integrityProfile = buildIntegrity(chat);
}

function buildIntegrity(chat) {
  const unresolvedCopies = (chat.messages||[]).reduce((n,m)=>n+(m.copyFields||[]).filter(f=>!f.resolved).length,0);
  const assets = (chat.messages||[]).flatMap(m=>m.assets||[]);
  const unresolvedAssets = assets.filter(a=>a.kind==='image' && !/^https?:\/\//i.test(a.url||'')).length;
  return {
    source: chat.parser === 'dom-fallback' ? 'DOM_FALLBACK' : 'SOURCE_OK',
    raw: currentSourceHtml ? 'RAW_PRESERVED' : (chat.parser==='manual-transcript' ? 'RAW_MANUAL_TEXT' : 'RAW_NOT_AVAILABLE'),
    uiBindings: unresolvedCopies ? 'UI_BINDINGS_PARTIAL' : 'UI_BINDINGS_RESOLVED_OR_NONE',
    assets: unresolvedAssets ? 'ASSETS_PARTIAL' : (assets.length ? 'ASSETS_RESOLVED' : 'ASSETS_NONE'),
    visualParity: 'NOT_CLAIMED'
  };
}

async function showSummary(chat) {
  const a = new Alert();
  a.title = t('Analysis complete', 'Analyse abgeschlossen');
  a.message = [
    `${t('Title','Titel')}: ${chat.title}`,
    `${t('Messages','Nachrichten')}: ${(chat.messages||[]).length}`,
    `${t('Parser','Parser')}: ${chat.parser}`,
    `${t('Participants','Teilnehmer')}: ${chat.participantCount || 0}`,
    `${t('Group chat','Gruppenchat')}: ${chat.isGroupChat ? 'YES' : 'NO'}`,
    `${t('Images','Bilder')}: ${collectImageAssets(chat).length}`,
    `${t('Integrity','Integrität')}: ${chat.integrityProfile.source} / ${chat.integrityProfile.assets}`
  ].join('\n');
  a.addAction(t('Continue', 'Weiter'));
  a.addAction(t('Export now', 'Jetzt exportieren'));
  a.addAction(t('Images', 'Bilder'));
  const i = await a.presentAlert();
  if (i === 1) await exportMenu();
  if (i === 2) await imageMenu();
}

async function showCurrentStructure() {
  if (!currentChat) { await info(t('No chat loaded yet.', 'Noch kein Chat geladen.')); return; }
  const table = new UITable();
  table.showSeparators = true;
  const head = new UITableRow(); head.isHeader = true; head.addText(`${currentChat.title} · ${currentChat.messages.length} ${t('messages','Nachrichten')}`); table.addRow(head);
  for (let i=0;i<currentChat.messages.length;i++) {
    const m = currentChat.messages[i];
    const row = new UITableRow();
    row.addText(`#${i+1} ${m.participantDisplayName || m.author}`, `${m.role} · ${m.contentType || 'text'} · ${(m.renderedText||'').slice(0,100)}`);
    row.onSelect = async () => { await showMessageStructure(m, i); };
    table.addRow(row);
  }
  await table.present(false);
}

async function showMessageStructure(m, i) {
  const payload = structureMessage(m, i);
  const a = new Alert();
  a.title = `#${i+1} ${m.participantDisplayName || m.author}`;
  a.message = JSON.stringify(payload, null, 2).slice(0, 7000);
  a.addAction(t('Save Message JSON', 'Nachricht-JSON speichern'));
  a.addAction(t('Copy JSON', 'JSON kopieren'));
  a.addCancelAction(t('Close', 'Schließen'));
  const c = await a.presentAlert();
  if (c === 0) {
    const path = uniquePath(rootDir, `message_${String(i+1).padStart(4,'0')}`, '.structure.json');
    fm.writeString(path, JSON.stringify(payload,null,2)); await verifyText(path, JSON.stringify(payload,null,2)); await shareOrDone([path]);
  }
  if (c === 1) Pasteboard.copyString(JSON.stringify(payload,null,2));
}

function structureMessage(m, i) {
  return {index:i+1,id:m.id,role:m.role,author:m.author,participantId:m.participantId,participantDisplayName:m.participantDisplayName,participantKind:m.participantKind,participantUsername:m.participantUsername,participantResolution:m.participantResolution,recipient:m.recipient,status:m.status,contentType:m.contentType,createdAtUnix:m.createdAt,copyFields:m.copyFields||[],warnings:m.warnings||[],rawContent:m.rawContent||{},rawMetadata:m.rawMetadata||{},renderedText:m.renderedText||m.text||'',assets:m.assets||[]};
}

function structureSnapshot(chat) {
  return {schema:APP.structureSchema,schemaVersion:APP.structureSchemaVersion,tool:APP.name,toolVersion:APP.version,exportedAt:new Date().toISOString(),title:chat.title,sourceUrl:chat.sourceUrl||'',parser:chat.parser,parserDetails:chat.parserDetails||'',primaryError:chat.primaryError||null,conversationType:chat.conversationType,isGroupChat:chat.isGroupChat,participantCount:chat.participantCount,participants:chat.participants||[],integrityProfile:chat.integrityProfile||{},messages:(chat.messages||[]).map(structureMessage)};
}

async function imageMenu() {
  if (!currentChat) { await info(t('Load or import a chat first.', 'Lade oder importiere zuerst einen Chat.')); return; }
  const images = collectImageAssets(currentChat);
  if (!images.length) { await info(t('No chat images were detected in the structured source.', 'In der strukturierten Quelle wurden keine Chat-Bilder erkannt.')); return; }
  const a = new Alert();
  a.title = t('Chat Images', 'Chat-Bilder');
  a.message = t(`${images.length} image assets detected. Direct HTTP(S) images can be downloaded as real image files, not Base64. Internal pointers are preserved as metadata.`, `${images.length} Bild-Assets erkannt. Direkte HTTP(S)-Bilder können als echte Bilddateien heruntergeladen werden, nicht als Base64. Interne Pointer bleiben als Metadaten erhalten.`);
  a.addAction(t('Browse / Download One', 'Einzeln ansehen / laden'));
  a.addAction(t('Download All Reachable', 'Alle erreichbaren laden'));
  a.addAction(t('Save Image Asset JSON', 'Bild-Asset-JSON speichern'));
  a.addCancelAction(t('Back', 'Zurück'));
  const i = await a.presentSheet();
  if (i === 0) await browseImages(images);
  if (i === 1) await downloadImages(images.filter(x=>/^https?:\/\//i.test(x.url||'')));
  if (i === 2) {
    const path=uniquePath(rootDir,'chat_images','.json'); const data=JSON.stringify(images,null,2); fm.writeString(path,data); await verifyText(path,data); await shareOrDone([path]);
  }
}

function collectImageAssets(chat) {
  const out=[];
  (chat.messages||[]).forEach((m,mi)=>(m.assets||[]).forEach((a,ai)=>{if(a.kind==='image'||String(a.mimeType||'').startsWith('image/'))out.push(Object.assign({messageIndex:mi+1,assetIndex:ai+1,author:m.participantDisplayName||m.author},a));}));
  return out;
}

async function browseImages(images) {
  const table = new UITable(); table.showSeparators=true;
  for (let i=0;i<images.length;i++) {
    const a=images[i], row=new UITableRow();
    row.addText(`#${i+1} ${a.name||'image'}`, `${a.author||''} · ${/^https?:\/\//i.test(a.url||'')?t('downloadable','downloadbar'):t('pointer only','nur Pointer')}`);
    row.onSelect = async()=>{ await imageAction(a,i); };
    table.addRow(row);
  }
  await table.present(false);
}

async function imageAction(asset, i) {
  const a=new Alert(); a.title=asset.name||`Image ${i+1}`; a.message=[`URL: ${asset.url||'-'}`,`Pointer: ${asset.assetPointer||'-'}`,`MIME: ${asset.mimeType||'-'}`].join('\n');
  if (/^https?:\/\//i.test(asset.url||'')) { a.addAction(t('Preview','Vorschau')); a.addAction(t('Download','Herunterladen')); }
  a.addAction(t('Copy Metadata','Metadaten kopieren')); a.addCancelAction(t('Close','Schließen'));
  const c=await a.presentAlert();
  if (/^https?:\/\//i.test(asset.url||'')) {
    if (c===0) { try { const img=await new Request(asset.url).loadImage(); await QuickLook.present(img); } catch(e){ await info(String(e)); } }
    if (c===1) await downloadImages([asset]);
    if (c===2) Pasteboard.copyString(JSON.stringify(asset,null,2));
  } else if (c===0) Pasteboard.copyString(JSON.stringify(asset,null,2));
}

async function downloadImages(images) {
  if (!images.length) { await info(t('No directly reachable images.', 'Keine direkt erreichbaren Bilder.')); return; }
  const dir = fm.joinPath(rootDir, `images_${dateStamp(new Date())}`); if(!fm.fileExists(dir)) fm.createDirectory(dir,true);
  const saved=[], failed=[];
  for (let i=0;i<images.length;i++) {
    const a=images[i];
    try {
      const r=new Request(a.url); r.timeoutInterval=CONFIG.REQUEST_TIMEOUT_SECONDS; const data=await r.load();
      const ext=guessExt(a); const name=safeFilename(a.name||`image_${i+1}`.replace(/\.[^.]+$/,'')); const path=uniquePath(dir,name,ext);
      fm.write(path,data); const rb=fm.read(path); if(rb.length!==data.length) throw new Error('binary readback mismatch'); saved.push(path);
    } catch(e){ failed.push({asset:a,error:String(e&&e.message||e)}); }
  }
  const receipt={saved:saved.map(p=>fm.fileName(p,true)),failed}; const receiptPath=fm.joinPath(dir,'download_receipt.json'); fm.writeString(receiptPath,JSON.stringify(receipt,null,2)); saved.push(receiptPath);
  await info(t(`${saved.length-1} image(s) saved. ${failed.length} failed.`, `${saved.length-1} Bild(er) gespeichert. ${failed.length} fehlgeschlagen.`));
  await shareOrDone(saved);
}

async function exportMenu() {
  if (!currentChat) { await info(t('No chat loaded yet.', 'Noch kein Chat geladen.')); return; }
  const a=new Alert(); a.title=t('Export','Exportieren');
  a.addAction('Markdown'); a.addAction('JSON'); a.addAction('JSONL'); a.addAction('JavaScript'); a.addAction(t('Structure JSON','Struktur-JSON')); a.addAction(t('All Formats + Source Folder','Alle Formate + Quellordner')); a.addCancelAction(t('Cancel','Abbrechen'));
  const i=await a.presentSheet(); if(i<0)return;
  if(i===0) await saveOne('md'); if(i===1) await saveOne('json'); if(i===2) await saveOne('jsonl'); if(i===3) await saveOne('js'); if(i===4) await saveOne('structure'); if(i===5) await saveAll();
}

async function saveOne(kind) {
  const base=exportBaseName(currentChat); let ext, data;
  if(kind==='md'){ext='.md';data=buildMarkdown(currentChat);}
  if(kind==='json'){ext='.json';data=JSON.stringify(machineExport(currentChat),null,2);}
  if(kind==='jsonl'){ext='.jsonl';data=buildJsonl(currentChat);}
  if(kind==='js'){ext='.js';data=`const CHAT_BACKUP = ${JSON.stringify(machineExport(currentChat),null,2)};\n`;}
  if(kind==='structure'){ext='.structure.json';data=JSON.stringify(structureSnapshot(currentChat),null,2);}
  const path=uniquePath(rootDir,base,ext); fm.writeString(path,data); await verifyText(path,data); lastSaved=[path]; await shareOrDone([path]);
}

async function saveAll() {
  const dir=fm.joinPath(rootDir, exportBaseName(currentChat)); if(!fm.fileExists(dir)) fm.createDirectory(dir,true);
  const files=[];
  const entries=[['chat.md',buildMarkdown(currentChat)],['chat.json',JSON.stringify(machineExport(currentChat),null,2)],['chat.jsonl',buildJsonl(currentChat)],['chat.js',`const CHAT_BACKUP = ${JSON.stringify(machineExport(currentChat),null,2)};\n`],['structure_inspector.json',JSON.stringify(structureSnapshot(currentChat),null,2)]];
  for(const [name,data] of entries){const p=fm.joinPath(dir,name);fm.writeString(p,data);await verifyText(p,data);files.push(p);}
  const sourceDir=fm.joinPath(dir,'source'); if(!fm.fileExists(sourceDir)) fm.createDirectory(sourceDir,true);
  const receipt={tool:APP.name,toolVersion:APP.version,parser:currentChat.parser,parserDetails:currentChat.parserDetails,primaryError:currentChat.primaryError||null,integrityProfile:currentChat.integrityProfile,sourceUrl:currentChat.sourceUrl||'',exportedAt:new Date().toISOString()};
  const rp=fm.joinPath(sourceDir,'parser_receipt.json');fm.writeString(rp,JSON.stringify(receipt,null,2));files.push(rp);
  const raw={version:2,exportedAt:new Date().toISOString(),sourceUrl:currentChat.sourceUrl||'',parser:currentChat.parser,parserDetails:currentChat.parserDetails,title:currentChat.title,shareId:currentChat.shareId,participants:currentChat.participants,messages:currentChat.messages.map(m=>({id:m.id,role:m.role,author:m.author,participantId:m.participantId,participantDisplayName:m.participantDisplayName,createdAt:m.createdAt,contentType:m.contentType,rawContent:m.rawContent,rawMetadata:m.rawMetadata,renderedText:m.renderedText,copyFields:m.copyFields,warnings:m.warnings,assets:m.assets}))};
  const rawp=fm.joinPath(sourceDir,'conversation.raw.json');fm.writeString(rawp,JSON.stringify(raw,null,2));files.push(rawp);
  if(currentSourceHtml && currentSourceHtml.length<=CONFIG.MAX_RAW_HTML_CHARS){const hp=fm.joinPath(sourceDir,'share-source.html');fm.writeString(hp,currentSourceHtml);files.push(hp);}
  if(settings.saveImages){const images=collectImageAssets(currentChat).filter(x=>/^https?:\/\//i.test(x.url||'')); if(images.length){const idir=fm.joinPath(dir,'assets');if(!fm.fileExists(idir))fm.createDirectory(idir,true);for(let i=0;i<images.length;i++){try{const data=await new Request(images[i].url).load();const p=uniquePath(idir,safeFilename(images[i].name||`image_${i+1}`),guessExt(images[i]));fm.write(p,data);files.push(p);}catch(_){}}}}
  const manifest={tool:APP.name,version:APP.version,createdAt:new Date().toISOString(),note:'Scriptable has no native ZIP writer. This is a portable iCloud folder. Use Share Sheet / Files to compress the folder if desired.',files:files.map(p=>({path:p.replace(dir+'/',''),size:fm.fileSize(p)}))};
  const mp=fm.joinPath(dir,'package_manifest.json');fm.writeString(mp,JSON.stringify(manifest,null,2));files.push(mp);
  lastSaved=files; await info(t(`Portable folder saved with ${files.length} files.`, `Portabler Ordner mit ${files.length} Dateien gespeichert.`)); await shareOrDone(files.slice(0,Math.min(files.length,20)));
}

function machineExport(chat) {
  return {schema:APP.schema,schemaVersion:APP.schemaVersion,tool:APP.name,toolVersion:APP.version,exportedAt:new Date().toISOString(),title:chat.title,source:{url:chat.sourceUrl||'',shareId:chat.shareId||'',parser:chat.parser,parserDetails:chat.parserDetails||'',primaryError:chat.primaryError||null},conversation:{type:chat.conversationType,isGroupChat:chat.isGroupChat,participantCount:chat.participantCount,participants:chat.participants||[],updatedAt:chat.updatedAt||null,integrityProfile:chat.integrityProfile||{}},messages:(chat.messages||[]).map((m,i)=>structureMessage(m,i)),assets:(chat.messages||[]).flatMap(m=>m.assets||[])};
}
function buildJsonl(chat){const rows=[{type:'metadata',data:Object.assign({},machineExport(chat),{messages:undefined})}];(chat.messages||[]).forEach((m,i)=>rows.push({type:'message',data:structureMessage(m,i)}));return rows.map(x=>JSON.stringify(x)).join('\n')+'\n';}
function buildMarkdown(chat){const L=[`# ${chat.title}`,'',`- **Source:** ${chat.sourceUrl||t('Manual import','Manueller Import')}`,`- **Exported:** ${new Date().toLocaleString()}`,`- **Messages:** ${chat.messages.length}`,`- **Parser:** ${chat.parser}`,`- **Participants:** ${chat.participantCount}`,`- **Group chat:** ${chat.isGroupChat?'YES':'NO'}`,'','---',''];chat.messages.forEach((m,i)=>{L.push(`## ${m.participantDisplayName||m.author}`,'',m.renderedText||m.text||'','');if(i!==chat.messages.length-1)L.push('---','');});L.push('','---','','## Export Integrity','',`- **Source:** ${chat.integrityProfile.source}`,`- **Raw:** ${chat.integrityProfile.raw}`,`- **UI bindings:** ${chat.integrityProfile.uiBindings}`,`- **Assets:** ${chat.integrityProfile.assets}`,`- **Visual parity:** ${chat.integrityProfile.visualParity}`,'','=== EXPORT COMPLETE ===');return L.join('\n').trim()+'\n';}

async function helpMenu() {
  const w=new WebView();
  const body = settings.language==='de' ? helpDE() : helpEN();
  await w.loadHTML(`<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#080414;color:#f7ecff;font-family:-apple-system;padding:18px;line-height:1.45}h1,h2{color:#ff2acb}code{color:#69f7ff}div.box{border:1px solid #a855f7;border-radius:12px;padding:12px;margin:12px 0;background:#14091f}</style></head><body>${body}</body></html>`);
  await w.present(true);
}
function helpEN(){return `<h1>666 ChatBackup Scriptable iPhone</h1><div class="box"><b>Public share:</b> Open ChatGPT → Share → Copy link → return to this script → Public Share Link. The importer automatically handles structured React-Flight shares and newer server-rendered transcript shares.</div><h2>Private chats</h2><p>A private <code>/c/</code> link is not downloadable without your authenticated ChatGPT session. Open the chat, copy the complete visible transcript, then use <b>Private / Manual Import</b>. The script analyzes role markers and rebuilds structured messages. It does not invent turns when markers are missing.</p><h2>When ChatGPT says the chat is full</h2><p>Sharing may temporarily stop working. An observed, non-guaranteed workaround is to submit one short extra prompt and use Share / Copy link during the brief period while ChatGPT starts processing. If that window is unavailable, use Manual Import.</p><h2>Group chats</h2><p>Explicit participant names/IDs are preserved. Manual transcripts such as <code>Alice:</code>, <code>Bob:</code>, <code>ChatGPT:</code> are reconstructed as separate participants. Unknown identities remain unresolved rather than guessed.</p><h2>Images</h2><p>Direct HTTP(S) chat images can be previewed and downloaded as real binary image files. Internal ChatGPT asset pointers without public bytes are preserved as metadata only. They are not Base64-invented.</p><h2>Exports</h2><p>Markdown, JSON, JSONL, JavaScript and Structure JSON are available. “All Formats + Source Folder” writes a portable iCloud folder with raw source artifacts and reachable image files. Scriptable does not provide a native ZIP writer; compress the saved folder in the Files app if you need a ZIP.</p><h2>Language</h2><p>English is default. Your selection is persisted in iCloud settings.</p>`;}
function helpDE(){return `<h1>666 ChatBackup Scriptable iPhone</h1><div class="box"><b>Öffentlicher Share:</b> ChatGPT öffnen → Teilen → Link kopieren → zurück zum Skript → Öffentlicher Share-Link. Der Importer verarbeitet automatisch strukturierte React-Flight-Shares und neuere serverseitig gerenderte Transcript-Shares.</div><h2>Private Chats</h2><p>Ein privater <code>/c/</code>-Link kann ohne deine angemeldete ChatGPT-Sitzung nicht heruntergeladen werden. Öffne den Chat, kopiere den kompletten sichtbaren Verlauf und verwende <b>Privat / Manuell importieren</b>. Das Skript analysiert Rollenmarker und baut strukturierte Nachrichten. Fehlen sichere Marker, werden keine Nachrichten erfunden.</p><h2>Wenn ChatGPT „Chat voll“ meldet</h2><p>Das Teilen kann vorübergehend nicht mehr funktionieren. Ein beobachteter, nicht garantierter Workaround: eine kurze zusätzliche Eingabe senden und das kurze Zeitfenster nutzen, während ChatGPT wieder zu verarbeiten beginnt. Wenn das nicht funktioniert, Manual Import verwenden.</p><h2>Gruppenchats</h2><p>Explizite Teilnehmernamen/-IDs bleiben erhalten. Manuelle Verläufe wie <code>Alice:</code>, <code>Bob:</code>, <code>ChatGPT:</code> werden als getrennte Teilnehmer rekonstruiert. Unbekannte Identitäten bleiben ungelöst statt geraten zu werden.</p><h2>Bilder</h2><p>Direkte HTTP(S)-Chatbilder können als echte Binärdateien angezeigt und heruntergeladen werden. Interne ChatGPT-Asset-Pointer ohne öffentliche Bytes bleiben nur als Metadaten erhalten. Es werden keine Base64-Bilder erfunden.</p><h2>Exporte</h2><p>Markdown, JSON, JSONL, JavaScript und Struktur-JSON sind verfügbar. „Alle Formate + Quellordner“ erzeugt einen portablen iCloud-Ordner mit Raw-Source und erreichbaren Bilddateien. Scriptable besitzt keinen nativen ZIP-Writer; bei Bedarf den Ordner in der Dateien-App komprimieren.</p><h2>Sprache</h2><p>Englisch ist Standard. Die Auswahl wird in den iCloud-Einstellungen gespeichert.</p>`;}
async function manualCopyHelp(){await info(t('Open ChatGPT, open the complete conversation, select/copy the visible transcript, then return to Scriptable and choose Analyze Clipboard. For very long chats copy the largest complete transcript ChatGPT/browser makes available.', 'Öffne ChatGPT, öffne den kompletten Chat, markiere/kopiere den sichtbaren Verlauf und kehre zu Scriptable zurück. Wähle dann Zwischenablage analysieren. Bei sehr langen Chats kopiere den größtmöglichen vollständigen Verlauf.'));}

async function shareOrDone(paths){const a=new Alert();a.title=t('Saved','Gespeichert');a.message=paths.map(p=>fm.fileName(p,true)).join('\n');a.addAction(t('Done','Fertig'));a.addAction(t('Share','Teilen'));const i=await a.presentAlert();if(i===1)await ShareSheet.present(paths);}
async function verifyText(path,data){if(fm.readString(path)!==data)throw new Error(`Readback mismatch: ${path}`);}
async function info(msg){const a=new Alert();a.title=APP.name;a.message=String(msg);a.addAction('OK');await a.presentAlert();}
async function progressInfo(msg){console.log(msg);}

function findChatGptUrl(s){const found=String(s||'').match(/https?:\/\/(?:www\.)?(?:chatgpt\.com|chat\.openai\.com)\/[^\s<>"']+/gi)||[];return (found.find(u=>/\/(?:share|s|c)\//i.test(u))||found[0]||'').replace(/[),.;!?]+$/g,'');}
function normalizeChatGptUrl(s){let u=String(s||'').trim().replace(/^http:\/\//i,'https://').split('#')[0];if(!/^https:\/\/(?:www\.)?(?:chatgpt\.com|chat\.openai\.com)\//i.test(u))throw new Error(t('Not a ChatGPT URL.','Kein ChatGPT-Link.'));return u;}
function makeRequest(url){const r=new Request(url);r.method='GET';r.timeoutInterval=CONFIG.REQUEST_TIMEOUT_SECONDS;r.headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language':settings.language==='de'?'de-DE,de;q=0.9,en;q=0.8':'en-US,en;q=0.9,de;q=0.7','Referer':'https://chatgpt.com/'};return r;}
async function fetchWithRetry(url){let last;for(let i=0;i<CONFIG.DOWNLOAD_RETRIES;i++){try{const r=makeRequest(url);const html=await r.loadString();if(r.response&&r.response.statusCode>=400)throw new Error('HTTP '+r.response.statusCode);if(!html||html.length<500)throw new Error('Empty or incomplete HTML');return html;}catch(e){last=e;if(i<CONFIG.DOWNLOAD_RETRIES-1)await sleep((i+1)*750);}}throw last;}
function scriptsIn(html){const out=[],re=/<script\b[^>]*>([\s\S]*?)<\/script\b[^>]*>/gi;let m;while((m=re.exec(html)))out.push(m[1]||'');return out;}
function readStringLiteral(src,start){if(src[start]!=='"')return null;let esc=false;for(let i=start+1;i<src.length;i++){if(esc){esc=false;continue;}if(src[i]==='\\'){esc=true;continue;}if(src[i]==='"')return{text:src.slice(start,i+1),end:i+1};}return null;}
function readJsonValueLiteral(src,start){let i=start;while(/\s/.test(src[i]||''))i++;if(i>=src.length)return null;const first=src[i];if(first==='"')return readStringLiteral(src,i);if(first!=='['&&first!=='{')return null;const close=first==='['?']':'}';const end=findBalanced(src,i,first,close);return end>i?{text:src.slice(i,end),end}:null;}
function addFlightCandidate(out,candidate){if(!Array.isArray(candidate))return;out.push(candidate);if(candidate.length>=2&&typeof candidate[1]==='string'&&candidate[1].trim().startsWith('[')){try{const nested=JSON.parse(candidate[1].trim());if(Array.isArray(nested))out.push(nested);}catch(_){}}else if(candidate.length>=2&&Array.isArray(candidate[1]))out.push(candidate[1]);}
function flightLoaders(html){const out=[];const markers=['streamController.enqueue(','self.__next_f.push(','__next_f.push('];const sources=scriptsIn(html);sources.push(String(html||''));for(const src of sources){for(const marker of markers){let at=0;while((at=src.indexOf(marker,at))!==-1){const start=at+marker.length;const lit=readJsonValueLiteral(src,start);at=lit?lit.end:start+1;if(!lit)continue;try{const parsed=JSON.parse(lit.text);if(typeof parsed==='string'){const t=parsed.trim();if(t.startsWith('[')){try{addFlightCandidate(out,JSON.parse(t));}catch(_){}}}else addFlightCandidate(out,parsed);}catch(_){}}}}const seen=new Set();return out.filter(x=>{let k='';try{k=JSON.stringify(x);}catch(_){return true;}if(seen.has(k))return false;seen.add(k);return true;});}
function findBalanced(s,start,open,close){let d=0,q=null,esc=false;for(let i=start;i<s.length;i++){const c=s[i];if(q){if(esc){esc=false;continue;}if(c==='\\'){esc=true;continue;}if(c===q)q=null;continue;}if(c==='"'||c==="'"||c==='`'){q=c;continue;}if(c===open)d++;if(c===close){d--;if(d===0)return i+1;}}return -1;}
function isObj(v){return v!==null&&typeof v==='object'&&!Array.isArray(v);}
function decodeFlight(loader){const cache=new Map(),active=new Set();function key(k){if(typeof k==='string'&&/^_\d+$/.test(k)){const i=Number(k.slice(1));if(typeof loader[i]==='string')return loader[i];}return String(k);}function resolve(v){if(typeof v==='number'&&Number.isInteger(v)){if(cache.has(v))return cache.get(v);if(v<0)return null;if(v>=loader.length)return v;if(active.has(v))return null;active.add(v);const x=resolve(loader[v]);active.delete(v);cache.set(v,x);return x;}if(Array.isArray(v))return v.map(resolve);if(isObj(v)){const o={};for(const k of Object.keys(v))o[key(k)]=resolve(v[k]);return o;}return v;}const d={};for(let i=1;i+1<loader.length;i+=2){if(typeof loader[i]==='string'&&!Object.prototype.hasOwnProperty.call(d,loader[i]))d[loader[i]]=resolve(loader[i+1]);}return d;}
function looksConversation(v){return isObj(v)&&isObj(v.mapping)&&Array.isArray(v.linear_conversation);}
function findRoute(decoded){const ld=isObj(decoded.loaderData)?decoded.loaderData:{};const known=['routes/share.$shareId.($action)','routes/share.$shareId','routes/s.$shareId.($action)','routes/s.$shareId'];for(const k of known)if(isObj(ld[k]))return ld[k];const seen=new Set();function find(v,d){if(d>12||!v||typeof v!=='object'||seen.has(v))return null;seen.add(v);if(looksConversation(v.data)||(isObj(v.serverResponse)&&looksConversation(v.serverResponse.data)))return v;for(const k of Object.keys(v)){const r=find(v[k],d+1);if(r)return r;}return null;}return find(decoded,0);}
function readHtmlAttribute(tag,name){const re=new RegExp("\\b"+name+"\\s*=\\s*(?:\"([^\"]*)\"|'([^']*)'|([^\\s>]+))","i");const m=re.exec(String(tag||''));return m?(m[1]??m[2]??m[3]??''):'';}
function decodeHtmlEntities(value){return String(value||'').replace(/&#x([0-9a-f]+);/gi,(_,h)=>{try{return String.fromCodePoint(parseInt(h,16));}catch(_){return'';}}).replace(/&#(\d+);/g,(_,d)=>{try{return String.fromCodePoint(parseInt(d,10));}catch(_){return'';}}).replace(/&nbsp;/gi,' ').replace(/&lt;/gi,'<').replace(/&gt;/gi,'>').replace(/&quot;/gi,'"').replace(/&#39;|&apos;/gi,"'").replace(/&amp;/gi,'&');}
function findHtmlElementByAttribute(src,attrName){const re=new RegExp("<([a-z0-9]+)\\b[^>]*\\b"+attrName+"(?:\\s*=\\s*(?:\"[^\"]*\"|'[^']*'|[^\\s>]+))?[^>]*>","i");const text=String(src||'');const m=re.exec(text);if(!m)return null;const tag=m[1].toLowerCase(),start=m.index+m[0].length;const tr=new RegExp('</?'+tag+'\\b[^>]*>','gi');tr.lastIndex=start;let depth=1,t;while((t=tr.exec(text))){if(t[0][1]==='/')depth--;else if(!/\/\s*>$/.test(t[0]))depth++;if(depth===0)return{inner:text.slice(start,t.index),outerStart:m.index,outerEnd:tr.lastIndex,openTag:m[0],tag};}return null;}
function htmlFragmentToText(value){let x=String(value||'');let prev;do{prev=x;x=x.replace(/<!--[\s\S]*?-->/g,'').replace(/<(script|style)\b[\s\S]*?<\/\1>/gi,'');}while(x!==prev);x=x.replace(/<a\b[^>]*href\s*=\s*(?:"([^"]+)"|'([^']+)')[^>]*>([\s\S]*?)<\/a>/gi,(_,a,b,label)=>{const text=decodeHtmlEntities(String(label||'').replace(/<[^>]+>/g,'')).trim(),url=decodeHtmlEntities(a||b||'');return text?`[${text}](${url})`:url;});x=x.replace(/<br\s*\/?>/gi,'\n').replace(/<\/(?:p|div|section|article|h[1-6]|pre|blockquote|table|tr)>/gi,'\n').replace(/<li\b[^>]*>/gi,'\n- ').replace(/<\/li>/gi,'\n').replace(/<[^>]+>/g,'');return decodeHtmlEntities(x).replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();}
function extractSsrAssets(segment){const out=[],seen=new Set();const re=/<img\b[^>]*(?:src|data-src)\s*=\s*(?:"([^"]+)"|'([^']+)')[^>]*>/gi;let m;while((m=re.exec(String(segment||'')))){const url=decodeHtmlEntities(m[1]||m[2]||'').trim();if(!/^https?:\/\//i.test(url)||seen.has(url))continue;seen.add(url);out.push({kind:'image',name:'Chat image '+(out.length+1),mimeType:'',url,assetPointer:'',downloadable:true});}return out;}
function parseSsrTranscriptFromHtml(html,url){const root=findHtmlElementByAttribute(html,'data-conversation-transcript');if(!root)return null;const source=root.inner;const re=/<li\b[^>]*\bdata-message-role\s*=\s*(["'])(user|assistant)\1[^>]*>/gi;const starts=[];let m;while((m=re.exec(source)))starts.push({index:m.index,end:re.lastIndex,role:m[2],tag:m[0]});if(!starts.length)return null;const messages=[];let possiblyIncomplete=0;for(let i=0;i<starts.length;i++){const item=starts[i],end=i+1<starts.length?starts[i+1].index:source.length,segment=source.slice(item.index,end),body=item.role==='assistant'?(findHtmlElementByAttribute(segment,'data-assistant-markdown-root')||findHtmlElementByAttribute(segment,'data-assistant-markdown')):(findHtmlElementByAttribute(segment,'data-user-message-copy')||findHtmlElementByAttribute(segment,'data-submit-message-animation-target'));const text=htmlFragmentToText(body?body.inner:segment).replace(/^(ChatGPT said:|You said:|User said:|Benutzer:|Du:)\s*/i,'').trim();const assets=extractSsrAssets(segment);if(!text&&!assets.length)continue;const id=readHtmlAttribute(item.tag,'id');const isAssistant=item.role==='assistant';messages.push(makeMessage({id:id||`ssr-${i+1}`,role:item.role,author:isAssistant?'ChatGPT':t('User','Benutzer'),text,rawContent:{sourceText:text},rawMetadata:{sourceSsrTranscript:true,selector:'data-message-role'},contentType:'ssr-html',status:'ssr',recipient:'all',assets,participantId:isAssistant?'chatgpt':'',participantDisplayName:isAssistant?'ChatGPT':t('User','Benutzer'),participantKind:isAssistant?'assistant':'human',participantResolution:isAssistant?'ROLE_CONFIRMED':'UNRESOLVED'}));if(unclosedFence(text))possiblyIncomplete++;}if(!messages.length)return null;const participants=buildParticipants(messages);const titleMatch=/<title\b[^>]*>([\s\S]*?)<\/title>/i.exec(String(html||''));const title=titleMatch?htmlFragmentToText(titleMatch[1]):'ChatGPT Conversation';return{title:title||'ChatGPT Conversation',shareId:extractShareId(url),updatedAt:null,messages,participants,participantCount:participants.length,isGroupChat:false,conversationType:'direct',parser:'ssr-source-transcript',parserDetails:'Direct raw HTML transcript parser: data-conversation-transcript + data-message-role',stats:{sourceEntries:starts.length,exported:messages.length,skippedHidden:0,skippedRole:0,skippedRecipient:0,skippedEmpty:starts.length-messages.length,skippedDuplicate:0,possiblyIncomplete},warnings:[t('Direct SSR source recovery used; dynamic UI bindings and non-HTTP assets may be incomplete.','Direkte SSR-Quellwiederherstellung verwendet; dynamische UI-Bindungen und nicht direkt erreichbare Assets können unvollständig sein.')]};}
function parseConversation(html,url){let last=null;const loaders=flightLoaders(html);for(let i=0;i<loaders.length;i++){try{const decoded=decodeFlight(loaders[i]);const route=findRoute(decoded);if(!route)continue;const sr=isObj(route.serverResponse)?route.serverResponse:{};const data=isObj(sr.data)?sr.data:route.data;const chat=chatFromData(data,route,url);chat.parser='react-flight';chat.parserDetails=`Loader ${i+1}/${loaders.length}`;return chat;}catch(e){last=e;}}const m=/<script\b[^>]*id=["']__NEXT_DATA__["'][^>]*>([\s\S]*?)<\/script>/i.exec(html);if(m){try{const payload=JSON.parse(m[1]);const pp=payload.props&&payload.props.pageProps||{};const sr=pp.serverResponse||{};const data=sr.data||{};const chat=chatFromData(data,{},url);chat.parser='legacy-next-data';chat.parserDetails='__NEXT_DATA__';return chat;}catch(e){last=e;}}try{const ssr=parseSsrTranscriptFromHtml(html,url);if(ssr)return ssr;}catch(e){last=e;}throw last||new Error('No supported share data format found.');}
function chatFromData(data,route,url){if(!isObj(data))throw new Error('No conversation data');const mapping=isObj(data.mapping)?data.mapping:{};const seq=Array.isArray(data.linear_conversation)?data.linear_conversation:[];const stats={sourceEntries:seq.length,exported:0,skippedHidden:0,skippedRole:0,skippedRecipient:0,skippedEmpty:0,skippedDuplicate:0,possiblyIncomplete:0},messages=[],seen=new Set();for(const entry of seq){let node=null;if(isObj(entry)&&typeof entry.id==='string'&&isObj(mapping[entry.id]))node=mapping[entry.id];else if(isObj(entry)&&isObj(entry.message))node=entry;if(!isObj(node)||!isObj(node.message)){stats.skippedEmpty++;continue;}const msg=node.message,meta=isObj(msg.metadata)?msg.metadata:{};if(meta.is_visually_hidden_from_conversation===true){stats.skippedHidden++;continue;}const auth=isObj(msg.author)?msg.author:{};const role=typeof auth.role==='string'?auth.role:'assistant';if(role==='system'||role==='developer'||(role==='tool'&&!CONFIG.INCLUDE_TOOL_MESSAGES)){stats.skippedRole++;continue;}const recipient=typeof msg.recipient==='string'?msg.recipient:'all';if(role==='assistant'&&recipient!=='all'&&recipient!==''){stats.skippedRecipient++;continue;}const id=typeof msg.id==='string'?msg.id:'';if(id&&seen.has(id)){stats.skippedDuplicate++;continue;}const content=isObj(msg.content)?msg.content:{};const flat=flattenContent(content,msg);if(!flat.text.trim()&&!flat.assets.length){stats.skippedEmpty++;continue;}if(id)seen.add(id);const identity=resolveParticipant(msg,auth,role);const mm=makeMessage({id,role,author:identity.displayName,text:flat.text,rawContent:content,rawMetadata:meta,contentType:content.content_type||'',createdAt:typeof msg.create_time==='number'?msg.create_time:null,status:typeof msg.status==='string'?msg.status:'',recipient,assets:flat.assets,participantId:identity.id,participantDisplayName:identity.displayName,participantKind:identity.kind,participantUsername:identity.username,participantResolution:identity.resolution});messages.push(mm);if(role==='assistant'&&msg.status&&msg.status!=='finished_successfully')stats.possiblyIncomplete++;if(unclosedFence(flat.text))stats.possiblyIncomplete++;}stats.exported=messages.length;const participants=buildParticipants(messages), humans=participants.filter(p=>p.kind==='human'&&p.resolution!=='UNRESOLVED');return{title:String(data.title||'ChatGPT Conversation'),shareId:String(route.sharedConversationId||data.conversation_id||extractShareId(url)||'shared'),updatedAt:typeof data.update_time==='number'?data.update_time:null,messages,participants,participantCount:participants.length,isGroupChat:Boolean(data.is_group_conversation||data.group_id||humans.length>=2),conversationType:(data.is_group_conversation||data.group_id||humans.length>=2)?'group':'direct',stats,warnings:[]};}
function resolveParticipant(msg,auth,role){const meta=isObj(msg.metadata)?msg.metadata:{};const candidates=[auth.name,auth.display_name,auth.username,meta.author_name,meta.display_name,meta.participant_name,meta.user_name].filter(x=>typeof x==='string'&&x.trim());const display=candidates[0]|| (role==='assistant'?'ChatGPT':t('User','Benutzer'));const id=String(auth.id||auth.user_id||meta.participant_id||meta.user_id||meta.author_id||'').trim();return{id:id||'',displayName:display,username:String(auth.username||meta.username||''),kind:role==='assistant'?'assistant':role==='tool'?'tool':'human',resolution:(id||candidates.length)?'SOURCE_IDENTITY':'UNRESOLVED'};}
function flattenContent(content,msg){const type=String(content.content_type||''),chunks=[],assets=[];if(type==='text'||(!type&&Array.isArray(content.parts))||type==='multimodal_text'){for(const part of(Array.isArray(content.parts)?content.parts:[])){if(typeof part==='string'){chunks.push(extractTextPart(part));continue;}if(!isObj(part))continue;const pt=String(part.content_type||part.type||'');if(pt==='image_asset_pointer'){const pointer=String(part.asset_pointer||part.assetPointer||'');const url=String(part.url||part.download_url||part.asset_url||'');assets.push({kind:'image',name:String(part.name||'Chat image'),mimeType:String(part.mime_type||part.mimeType||'image/*'),url:/^https?:\/\//i.test(url)?url:'',assetPointer:pointer,downloadable:/^https?:\/\//i.test(url)});chunks.push('*[Image from original chat]*');continue;}if(pt==='file'){const url=String(part.download_url||part.file_url||part.url||'');assets.push({kind:'file',name:String(part.name||'Attachment'),mimeType:String(part.mime_type||''),url:/^https?:\/\//i.test(url)?url:'',assetPointer:String(part.asset_pointer||''),downloadable:/^https?:\/\//i.test(url)});chunks.push(`*[Attachment: ${part.name||'file'}]*`);continue;}chunks.push(extractTextPart(part));}}else if(type==='code'){chunks.push('```'+(content.language||'')+'\n'+String(content.text||'')+'\n```');}else if(type==='reasoning_recap'){if(typeof content.content==='string')chunks.push('_'+content.content+'_');}else if(type==='thoughts'){for(const th of(content.thoughts||[])){if(isObj(th)&&typeof th.summary==='string')chunks.push('_'+th.summary+'_');}}else if(type==='tool_response'){if(CONFIG.INCLUDE_TOOL_MESSAGES&&typeof content.output==='string')chunks.push(content.output);}else if(typeof content.text==='string')chunks.push(content.text);const atts=isObj(msg.metadata)&&Array.isArray(msg.metadata.attachments)?msg.metadata.attachments:[];for(const a of atts){if(!isObj(a))continue;const url=String(a.download_url||a.file_url||'');const mime=String(a.mime_type||a.content_type||'');const kind=mime.startsWith('image/')?'image':'file';assets.push({kind,name:String(a.name||'Attachment'),mimeType:mime,url:/^https?:\/\//i.test(url)?url:'',assetPointer:String(a.asset_pointer||a.file_id||''),downloadable:/^https?:\/\//i.test(url)});chunks.push(/^https?:\/\//i.test(url)?`[${a.name||'Attachment'}](${url})`:`*[Attachment: ${a.name||'Attachment'}]*`);}return{text:chunks.filter(x=>typeof x==='string'&&x.length).join('\n\n'),assets};}
function extractTextPart(p){if(typeof p==='string'){const s=p.trim();if(s.startsWith('{')&&s.endsWith('}')){try{const o=JSON.parse(s);if(isObj(o)&&typeof o.response==='string')return o.response;if(isObj(o)&&typeof o.content==='string')return o.content;}catch(_){}}return p;}if(isObj(p)){if(typeof p.text==='string')return p.text;if(Array.isArray(p.text))return p.text.filter(x=>typeof x==='string').join('\n');}return '';}
function extractCopyFields(source){const literals=new Map(),fields=[],warnings=[];const decl=/\b(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=\s*/g;let m;while((m=decl.exec(source))){const at=decl.lastIndex,q=source[at];if(q!=='`'&&q!=='"'&&q!=="'")continue;const lit=readJsLiteral(source,at);if(!lit)continue;if(lit.dynamic){warnings.push('Dynamic template expression unresolved: '+m[1]);continue;}literals.set(m[1],lit.value);decl.lastIndex=lit.end;}const copied=new Set(),re=/GenUI\.copy\s*\(\s*([A-Za-z_$][\w$]*)\s*\)/g;while((m=re.exec(source))){const id=m[1];if(copied.has(id))continue;copied.add(id);const v=literals.get(id);fields.push({identifier:id,label:guessField(id,source,m.index),resolved:typeof v==='string',text:typeof v==='string'?v:null,utf16Length:typeof v==='string'?v.length:null});}const unresolved=fields.filter(x=>!x.resolved).length;if(unresolved)warnings.push(`${unresolved} copy action(s) unresolved.`);return{fields,warnings};}
function readJsLiteral(src,at){const q=src[at];let esc=false,dyn=false,out='';for(let i=at+1;i<src.length;i++){const c=src[i];if(esc){if(c==='n')out+='\n';else if(c==='r')out+='\r';else if(c==='t')out+='\t';else out+=c;esc=false;continue;}if(c==='\\'){esc=true;continue;}if(q==='`'&&c==='$'&&src[i+1]==='{')dyn=true;if(c===q)return{value:out,end:i+1,dynamic:dyn};out+=c;}return null;}
function guessField(id,source,at){const k=id.toLowerCase();if(/main|haupt/.test(k))return'Main input';if(/extend/.test(k))return'Extended';if(/style/.test(k))return'Style';if(/lyric|structure/.test(k))return'Lyrics / Structure';if(/title|titel/.test(k))return'Title';return'Unknown';}
function renderMarkdownText(text){let s=String(text||'').replace(/\u0000/g,'');if(CONFIG.REMOVE_CHATGPT_CITATION_MARKERS)s=s.replace(/(?:cite|filecite|navlist|filenavlist)[^]*/g,'');return s.trim();}
function unclosedFence(text){return((String(text).match(/```/g)||[]).length%2)!==0;}
async function extractMessagesFromWebView(w, parserName, parserDetails, url) {
  const js = `(() => {
    const legacyRoleNodes = Array.from(document.querySelectorAll('[data-message-author-role]'));
    const legacyTurnNodes = Array.from(document.querySelectorAll('[data-testid^="conversation-turn-"]'));
    const ssrRoleNodes = Array.from(document.querySelectorAll('[data-message-role="user"], [data-message-role="assistant"]'));
    const transcriptRoots = Array.from(document.querySelectorAll('[data-conversation-transcript]'));
    const candidates = ssrRoleNodes.length ? ssrRoleNodes : (legacyRoleNodes.length ? legacyRoleNodes : legacyTurnNodes);
    const r = [], seen = new Set();

    for (const candidate of candidates) {
      const ssrRoot = candidate.closest('[data-message-role="user"], [data-message-role="assistant"]');
      const legacyRoot = candidate.closest('[data-testid^="conversation-turn-"]') || candidate.closest('article');
      const root = ssrRoot || legacyRoot || candidate;
      if (seen.has(root)) continue;

      let role = '';
      if (root.hasAttribute && root.hasAttribute('data-message-role')) {
        role = root.getAttribute('data-message-role') || '';
      }
      if (role !== 'user' && role !== 'assistant') {
        const roleNode = root.matches && root.matches('[data-message-author-role]')
          ? root
          : root.querySelector('[data-message-author-role]');
        role = roleNode && roleNode.getAttribute('data-message-author-role') || '';
      }
      if (role !== 'user' && role !== 'assistant') continue;

      let body = null;
      if (role === 'assistant') {
        body = root.querySelector('[data-assistant-markdown-root], [data-assistant-markdown], .markdown, [class*="markdown"]');
      } else {
        body = root.querySelector('[data-user-message-copy], [data-submit-message-animation-target], .markdown, [class*="markdown"]');
      }
      if (!body) {
        body = root.querySelector('[data-message-author-role]') || root;
      }

      let txt = String(body && (body.innerText || body.textContent) || '').replace(/\\n{3,}/g,'\\n\\n').trim();
      if (!txt) continue;

      if (body === root) {
        txt = txt.replace(/^(ChatGPT said:|You said:|User said:|Benutzer:|Du:)\\s*/i,'').trim();
      }

      seen.add(root);
      r.push({
        role,
        text: txt,
        id: root.getAttribute('id') || root.getAttribute('data-testid') || root.getAttribute('data-message-id') || 'dom-' + (r.length + 1)
      });
    }

    const meta=document.querySelector('meta[property="og:title"]');
    return {
      items:r,
      title:(meta&&meta.content)||document.title||'ChatGPT Conversation',
      diagnostics:{
        title:document.title,
        path:location.pathname,
        readyState:document.readyState,
        legacyRoleNodes:legacyRoleNodes.length,
        legacyTurnNodes:legacyTurnNodes.length,
        ssrRoleNodes:ssrRoleNodes.length,
        transcriptRoots:transcriptRoots.length,
        bodyChars:String(document.body&&document.body.innerText||'').length
      }
    };
  })()`;
  let result = null;
  for (let attempt = 0; attempt < 3; attempt++) {
    result = await w.evaluateJavaScript(js, false);
    if (result && Array.isArray(result.items) && result.items.length) break;
    if (attempt < 2) await sleep(900);
  }
  const items = result && result.items;
  if (!Array.isArray(items) || !items.length) {
    const d = result && result.diagnostics || {};
    throw new Error('DOM_NO_MESSAGES ' + JSON.stringify(d).slice(0,500));
  }
  const messages = items.map((x,i) => makeMessage({id:x.id||`dom-${i+1}`, role:x.role,author:x.role==='assistant'?'ChatGPT':t('User','Benutzer'), text:x.text,rawContent:{text:x.text}, rawMetadata:{domFallback:true,parser:parserName},contentType:'dom', status:'dom', recipient:'all'}));
  return {title:String(result.title||'ChatGPT Conversation').replace(/^ChatGPT\s*[-–—:]\s*/i,'').trim()||'ChatGPT Conversation',shareId:extractShareId(url),updatedAt:null,messages,participants:buildParticipants(messages),parser:parserName,parserDetails,stats:{sourceEntries:items.length,exported:items.length,skippedHidden:0,skippedRole:0,skippedRecipient:0,skippedEmpty:0,skippedDuplicate:0,possiblyIncomplete:0},warnings:[]};
}
async function extractViaFetchedHtml(html,url) {
  const w = new WebView();
  await w.loadHTML(String(html||''), url);
  return await extractMessagesFromWebView(w,'source-dom-fallback','Fetched HTML rendered locally in WebView, role-confirmed',url);
}
async function extractViaWebView(url) {
  const w = new WebView();
  await w.loadRequest(makeRequest(url));
  return await extractMessagesFromWebView(w,'dom-fallback','Live WebView text, role-confirmed',url);
}
function extractShareId(url){const m=String(url||'').match(/\/(?:share|s)\/([^/?#]+)/i);return m?m[1]:'shared';}
function safeFilename(s){return String(s||'ChatGPT_Conversation').normalize('NFKC').replace(/[\\/:*?"<>|]/g,'-').replace(/[\r\n\t]+/g,' ').replace(/\s+/g,'_').replace(/^[-_. ]+|[-_. ]+$/g,'').slice(0,80)||'ChatGPT_Conversation';}
function exportBaseName(chat){return safeFilename(chat.title).slice(0,60)+'_'+dateStamp(new Date())+'_'+String(chat.shareId||'chat').slice(0,8);}
function uniquePath(folder,base,ext){let n=0,p;do{p=fm.joinPath(folder,base+(n?'_'+(n+1):'')+ext);n++;}while(fm.fileExists(p));return p;}
function dateStamp(d){const p=n=>String(n).padStart(2,'0');return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())+'_'+p(d.getHours())+'-'+p(d.getMinutes())+'-'+p(d.getSeconds());}
function guessExt(a){const n=String(a.name||'').toLowerCase();if(/\.(png|jpe?g|webp|gif|bmp)$/.test(n))return'.'+n.split('.').pop();const m=String(a.mimeType||'').toLowerCase();if(m.includes('png'))return'.png';if(m.includes('jpeg')||m.includes('jpg'))return'.jpg';if(m.includes('webp'))return'.webp';if(m.includes('gif'))return'.gif';if(m.includes('bmp'))return'.bmp';return'.img';}
function sleep(ms){return new Promise(resolve=>Timer.schedule(Math.max(0,Number(ms)||0)/1000,false,resolve));}
