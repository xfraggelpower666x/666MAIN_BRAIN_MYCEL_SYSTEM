'use strict';
const el = (id) => document.getElementById(id);
const source = el('source');
const germanNames = {
  de: 'Deutsch', en: 'Englisch · International', 'en-US': 'Englisch · USA',
  'en-GB': 'Englisch · UK', es: 'Español', 'pt-BR': 'Português · Brasil'
};
const englishNames = {de:'German', en:'English · International', 'en-US':'English · US', 'en-GB':'English · UK', es:'Spanish', 'pt-BR':'Portuguese · Brazil'};
let names = englishNames;
const targetLocales={de:'de-DE',en:'en-GB','en-US':'en-US','en-GB':'en-GB',es:'es-ES','pt-BR':'pt-BR'};
const session = location.pathname.split('/')[1];
let lastRequest = null;
let currentResult = null;
let reviewRule = null;
let reviewRequest = null;
let busy = false;

function node(tag, text, className) {
  const item = document.createElement(tag);
  if (text !== undefined) item.textContent = text;
  if (className) item.className = className;
  return item;
}

async function api(path, data) {
  const headers = {'X-Lingua-Session': session};
  const options = {headers, cache: 'no-store'};
  if (data !== undefined) {
    options.method = 'POST';
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(data);
  }
  const response = await fetch('api/' + path, options);
  const result = await response.json();
  if (!response.ok) throw new Error(result.error ? localizedError(result.error) : t('Lokale Anfrage fehlgeschlagen.'));
  return result;
}

function status(message) { const output = el('global-status'); if (output) output.textContent = message; }
function request() {
  return {from: el('from').value, to: el('to').value, text: source.value, emoji: el('emoji').checked};
}
function refreshInput() {
  const pair = request();
  const count = Array.from(source.value).length;
  el('count').textContent = count.toLocaleString(locale()) + ' / '+(12000).toLocaleString(locale());
  el('pair').textContent = pair.from + ' → ' + pair.to;
  el('copy-source').disabled = !source.value.trim();
  el('translate').disabled = busy || !source.value.trim() || count > 12000 || pair.from === pair.to;
  el('learn').disabled = busy || !source.value.trim() || count > 12000 || pair.from === pair.to;
  el('previous').disabled = busy || !lastRequest;
}

function evidence(list, blocks, hasOutput) {
  const area = el('evidence');
  area.replaceChildren();
  for (const proof of list) {
    const item = node('li');
    item.append(node('span', [t(proof.kind), proof.ref].filter(Boolean).join(' · '), 'proof-ref'));
    item.append(document.createTextNode(' — ' + t(proof.reason)));
    if (proof.segment) item.append(node('q', proof.segment));
    const details = [
      [t('Beobachtete Hinweise'), proof.signals],
      [t('Geprüfte Lesarten'), proof.alternatives],
      [t('Gewählte Fassung'), proof.selected ? [proof.selected] : []]
    ];
    for (const [label, values] of details) {
      if (values?.length) item.append(node('div', label + ' · ' + values.join(' / '), 'proof-detail'));
    }
    area.append(item);
  }
  el('coverage').textContent = list.length + ' ' + t(list.length === 1 ? 'Beleg' : 'Belege');
  el('show-evidence').dataset.state = blocks ? 'blocked' : (hasOutput ? 'checked' : '');
  el('step-input').dataset.state = 'ok';
  el('step-match').dataset.state = blocks ? 'fail' : 'ok';
  el('step-output').dataset.state = hasOutput ? 'ok' : 'fail';
}

async function copy(value, message = 'Zielfassung kopiert.') {
  try {
    await navigator.clipboard.writeText(value);
    status(t(message));
  } catch {
    status(t('Zwischenablage nicht verfügbar. Text markieren und mit Strg+C kopieren.'));
  }
}

function render(result) {
  const container = el('variants');
  const alternatives = el('alternate-variants');
  container.replaceChildren();
  alternatives.replaceChildren();
  el('out-status').dataset.status = result.status;
  el('out-status').textContent = ({
    ABGELEITET: t('ÜBERSETZT'), IDENTITÄT: t('IDENTITÄT GEPRÜFT'),
    LINGUA_TRANSLATION_BLOCKED: t('BLOCKIERT')
  })[result.status] || result.status;
  const variants = result.variants || [];
  const empty = el('empty');
  empty.hidden = variants.length > 0;
  if (!empty.hidden) empty.querySelector('p').textContent =
    t('Kein vollständiger Treffer. Prüfe die markierten Abschnitte oder bestätige eine eigene Fassung.');
  for (const variant of variants) {
    if (variant.id === 'PRIMARY') {
      const box = node('textarea', variant.text, 'target-text');
      box.readOnly = true;
      box.setAttribute('aria-label', t('Hauptübersetzung'));
      container.append(box);
      continue;
    }
    const entry = node('article', undefined, 'variant');
    entry.append(node('h3', t(variant.label)), node('p', variant.text));
    if (variant.note) entry.append(node('small', t(variant.note), 'note'));
    const button = node('button', t('Kopieren'), 'copy');
    button.type = 'button';
    button.addEventListener('click', () => copy(variant.text));
    entry.append(button);
    alternatives.append(entry);
  }
  el('copy-target').disabled = !container.querySelector('.target-text')?.value;
  const blocked=result.evidence.some((proof) => proof.kind === 'OFFEN');
  evidence(result.evidence,blocked,variants.length>0);
  el('show-alternatives').disabled = variants.length < 2;
}

function clearResult() {
  currentResult = null;
  el('copy-target').disabled = true;
  el('variants').replaceChildren();
  el('alternate-variants').replaceChildren();
  el('show-alternatives').disabled = true;
  el('show-evidence').dataset.state = '';
  el('empty').hidden = false;
  el('empty').querySelector('p').textContent = t('Die Fassungen erscheinen nach der Übersetzung.');
  el('out-status').dataset.status = '';
  el('out-status').textContent = t('BEREIT');
  el('evidence').replaceChildren(node('li',t('Hier erscheinen Treffer, blockierte Abschnitte und die Gründe für die Ausgabe.')));
  el('coverage').textContent = t('0 Belege');
  for (const id of ['step-input','step-match','step-output']) el(id).dataset.state = '';
}
async function translate() {
  if (el('translate').disabled) return;
  const current = request();
  busy = true;
  clearResult();
  refreshInput();
  status(t('Prüfe lokale Sprachbelege …'));
  try {
    const result = await api('translate', current);
    lastRequest = current;
    if (JSON.stringify(request()) === JSON.stringify(current)) {
      currentResult = {request: current, result};
      render(result);
      status('');
    } else status(t('Eingabe geändert. Die neue Fassung kann jetzt übersetzt werden.'));
  } catch (error) {
    status(error.message);
  } finally {
    busy = false;
    refreshInput();
  }
}

async function hash(text) {
  const value = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(value), (byte) => byte.toString(16).padStart(2,'0')).join('');
}
function normalized(text) {
  return text.replace(/[’‘]/g,"'").replace(/[–—]/g,'-').trim().replace(/\s+/g,' ').toLowerCase();
}
async function beginReview(rule = null, target = null) {
  const current = rule ? {from: rule.from, to: rule.to, text: rule.source, emoji: false} : request();
  if (el('review').open) return;
  try {
    if (!rule) {
      const rules = await api('memory');
      rule = rules.find((item) => item.from === current.from && item.to === current.to &&
        normalized(item.source) === normalized(current.text)) || null;
    }
    reviewRule = rule;
    reviewRequest = current;
    el('review-pair').textContent = names[current.from] + ' → ' + names[current.to];
    el('review-source').textContent = current.text;
    el('review-text').value = rule?.target || target || '';
    el('review-status').textContent = '';
    el('review').showModal();
    el('review-text').focus();
  } catch (error) { status(error.message); }
}
async function saveReview() {
  const button = el('save');
  button.disabled = true;
  try {
    const previous = reviewRule ? await hash(reviewRule.target) : '';
    await api('confirm', {...reviewRequest, target: el('review-text').value, previous});
    el('review').close();
    const message = t('Lokal bestätigt. Die Fassung wird bei gleicher Eingabe bevorzugt.');
    if (el('memory').open) {
      await loadMemory();
      el('memory-status').textContent = message;
      el('refresh').focus();
    } else {
      await translate();
      status(message);
    }
  } catch (error) { el('review-status').textContent = error.message; }
  finally { button.disabled = false; }
}

async function loadMemory() {
  const area = el('rules');
  area.replaceChildren(node('p',t('Lade bestätigte Fassungen …')));
  try {
    const rules = await api('memory');
    area.replaceChildren();
    if (!rules.length) area.append(node('p',t('Noch keine Zielfassung bestätigt.')));
    for (const rule of rules) {
      const card = node('article', undefined, 'rule');
      const localDate = new Date(rule.created).toLocaleString(locale());
      card.append(node('small',rule.from+' → '+rule.to+' · '+localDate),node('p', rule.source),node('p',rule.target));
      const edit = node('button',t('Bearbeiten'),'quiet');
      const remove = node('button',t('Löschen'),'quiet');
      edit.type = remove.type = 'button';
      edit.addEventListener('click', () => beginReview(rule));
      remove.addEventListener('click', async () => {
        if (!confirm(t('Diese bestätigte Fassung dauerhaft löschen?'))) return;
        const feedback = el('memory-status');
        try {
          await api('forget', {id:rule.id, previous:await hash(rule.target)});
          await loadMemory();
          feedback.textContent = t('Fassung gelöscht.');
          if (el('memory').open) el('refresh').focus();
        } catch (error) { feedback.textContent = error.message; }
      });
      const actions = node('div', undefined,'actions');
      actions.append(edit, remove);
      card.append(actions);
      area.append(card);
    }
  } catch (error) { area.replaceChildren(node('p',error.message)); }
}

function updateLanguageOptions() {
  names=uiLanguage==='de'?germanNames:englishNames;
  for(const id of ['from','to','partner-language']){
    const select=el(id);
    const prior=select.value;
    select.replaceChildren();
    for(const [profile,name] of Object.entries(names)){
      const option=node('option',name);
      option.value=profile;
      select.append(option);
    }
    select.value=prior || (id==='from'?'en':'de');
  }
}
updateLanguageOptions();
for (const id of ['from','to','emoji']) el(id).addEventListener('change', () => {clearResult(); refreshInput();});
source.addEventListener('input', () => {clearResult(); refreshInput();});
el('swap').addEventListener('click', () => {
  [el('from').value, el('to').value] = [el('to').value, el('from').value];
  clearResult(); refreshInput();
});
el('translate').addEventListener('click',translate);
el('copy-source').addEventListener('click', () => copy(source.value, 'Quelltext kopiert.'));
el('copy-target').addEventListener('click', () => {
  const value = el('variants').querySelector('.target-text')?.value;
  if (value) copy(value);
});
document.addEventListener('keydown',(event) => {
  if (event.ctrlKey && event.key === 'Enter' && !document.querySelector('dialog[open]')) {
    event.preventDefault(); translate();
  }
});
el('previous').addEventListener('click', () => {
  if (lastRequest) source.value = lastRequest.text;
  clearResult(); refreshInput();
  status(t('Letzter Quelltext aus diesem Fenster übernommen.'));
  source.focus();
});
el('learn').addEventListener('click', () => {
  const current = currentResult;
  const cleanTarget = current?.result.plain || null;
  beginReview(null, cleanTarget);
});
el('save').addEventListener('click', saveReview);
el('refresh').addEventListener('click', loadMemory);
el('quit').addEventListener('click', async () => {
  try {
    await api('quit', {});
    document.querySelector('main').replaceChildren(node('p',t('666LINGUA wurde beendet. Dieses Fenster kann geschlossen werden.')));
    el('quit').disabled = true;
  } catch (error) { status(error.message); }
});
for (const trigger of document.querySelectorAll('[data-panel]')) {
  trigger.addEventListener('click', () => {
    const id = trigger.dataset.panel;
    if (id === 'translation') {
      source.focus();
      return;
    }
    const overlay = el(id);
    if (overlay.open) return;
    overlay.showModal();
    if (id === 'memory') {
      el('memory-status').textContent = '';
      loadMemory();
    }
    if (id === 'dictionary') loadDictionary();
  });
}
for (const button of document.querySelectorAll('[data-close]')) {
  button.addEventListener('click', () => button.closest('dialog').close());
}

let systemInfo;
function updateSystemInfo() {
  if(!systemInfo)return;
  el('release-label').textContent='DESKTOP '+systemInfo.version+' / R19';
  el('system-info').replaceChildren();
  const lines=[
    ['Windows-Ausgabe',systemInfo.version],['Quellenstand',systemInfo.source],
    ['Native Live-Quelle','3.4.6 / R18 · '+t('Live-State und MAIN-Artefakt geprüft.')],
    ['Autorität',t('Lokaler Windows-Ableger · R19 unveröffentlicht')],
    ['Externe Abnahme',t('MUM-KI-Host-Abnahme offen')]
  ];
  for(const [key,value] of lines) el('system-info').append(node('dt',t(key)),node('dd',value));
}
api('info').then(info=>{systemInfo=info;updateSystemInfo();}).catch(error=>status(error.message));
refreshInput();
