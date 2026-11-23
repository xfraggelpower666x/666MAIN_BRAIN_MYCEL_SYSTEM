(() => {
  const shell = document.getElementById('sceeri-ui-navigation');
  const data = JSON.parse(shell.querySelector('[data-ui-data]').textContent);
  const buttons = [...shell.querySelectorAll('[data-ui-mode]')];
  const panels = new Map(buttons.map((button) => [button.dataset.uiMode, document.getElementById(button.getAttribute('aria-controls'))]));
  const field = (name) => shell.querySelector('[data-daemon-' + name + ']');
  const settings = data.companion || {};
  const knownModes = new Set(panels.keys());
  const key = settings.project_key ? 'scevi.visual.preference.v1:' + settings.project_key : null;
  const feedback = field('feedback');
  const actionText = field('action');
  const priority = ['readback', 'clarify', 'verify', 'navigate'];
  const criticalStates = ['CONFLICT_QUARANTINE', 'WRITE_BLOCKED', 'READBACK_PENDING', 'BLOCKIERT'];
  const actions = new Map((data.actions || []).map(action => [action.id, action]));
  const actionKey = key && settings.source_revision
    ? 'scevi.visual.action.v1:' + JSON.stringify([settings.project_key, settings.source_revision])
    : null;
  let preferredAction = null;
  let selectedAction = null;
  let projectView = data.views.find(view => view.id === settings.start_view) || data.views[0];
  let chart = { state:'OFFEN', reason:'Messwerte, Einheiten und Quelle prüfen' };
  let formats = { id:null, form:'Handwritten', missing:null };
  let preference = null;
  let mode;

  function readPreference(storageKey, decode) {
    if (!storageKey) return null;
    let raw;
    try {
      raw = localStorage.getItem(storageKey);
    } catch {
      feedback.textContent = 'Ansichtsvorlieben gelten in dieser geöffneten Ansicht.';
      return null;
    }
    if (raw === null) return null;
    try {
      const value = raw.length <= 160 ? decode(JSON.parse(raw)) : null;
      if (value) return value;
    } catch {
      // Beschädigte Darstellungspräferenz kontrolliert entfernen.
    }
    try {
      localStorage.removeItem(storageKey);
      if (localStorage.getItem(storageKey) !== null) throw new Error('Rücklesen fehlgeschlagen');
      feedback.textContent = 'Ungültige Darstellungspräferenz bereinigt.';
    } catch {
      feedback.textContent = 'Ungültige Darstellungspräferenz in dieser Ansicht übersprungen.';
    }
    return null;
  }

  function completed(id) {
    const action = actions.get(id);
    return action.status === 'VERIFIZIERT' && (action.requires || []).every(completed);
  }

  function availableActions() {
    if (mode !== 'project') return [];
    return [...actions.values()].filter(action =>
      (!action.view_id || action.view_id === projectView.id) &&
      (!action.status || action.status === 'VORGESCHLAGEN') &&
      (action.requires || []).every(completed)
    ).sort((a, b) =>
      priority.indexOf(a.kind) - priority.indexOf(b.kind) ||
      Number(b.id === preferredAction) - Number(a.id === preferredAction)
    );
  }

  function recommendation() {
    const state = settings.status || projectView.status;
    const currentReason = projectView.source;
    const critical = criticalStates.find(value => value === settings.status || value === projectView.status);
    if (critical === 'READBACK_PENDING')
      return ['READBACK_PENDING', 'Zielstand rücklesen', settings.blocker || projectView.source];
    if (critical)
      return [critical, 'Blocker oder Konflikt prüfen', settings.blocker || projectView.source];
    if (settings.blocker) return ['BLOCKIERT', 'Blocker klären', settings.blocker];
    const options = availableActions();
    if (options.length) {
      const action = options.find(item => item.id === selectedAction) || options[0];
      return ['VORGESCHLAGEN', action.label, action.source, action, options];
    }
    if (mode === 'formats') {
      const label = formats.missing ? 'Offene Angaben in ' + formats.form + ' ergänzen' : formats.missing === 0 ? 'Auftrag für ' + formats.form + ' prüfen' : 'Visualform und Eingaben wählen';
      return ['VORGESCHLAGEN', label, 'Aktive Visualform · ' + formats.form];
    }
    if (mode === 'charts') return [chart.state, chart.reason, 'Aktuelle Eingabe in Intelligent Charts'];
    if (settings.next_step) return ['VORGESCHLAGEN', settings.next_step, settings.reason || projectView.source];
    if (state === 'OFFEN' || state === 'PARTIAL') return [state, 'Fehlenden Projektbeleg klären', currentReason];
    return ['VORGESCHLAGEN', 'Passende Gegenprobe festlegen', currentReason];
  }

  function render() {
    const [status, action, source, selected, options = []] = recommendation();
    const projectState = settings.status || projectView.status;
    const displayedState = ['BLOCKIERT', 'WRITE_BLOCKED', 'CONFLICT_QUARANTINE', 'READBACK_PENDING'].includes(status) ? status
      : mode === 'project' ? projectState : status;
    field('state').dataset.state = displayedState;
    field('state').textContent = settings.phase ? settings.phase + ' · ' + displayedState : displayedState;
    actionText.textContent = action;
    field('reason').textContent = selected ? selected.reason + ' · Quelle ' + source : source;
    field('effect').hidden = !selected;
    field('effect').textContent = selected ? 'Erwartete Wirkung · ' + selected.effect : '';
    const menu = field('options');
    menu.hidden = !options.length;
    menu.replaceChildren(...options.map(option => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = option.label;
      button.dataset.actionId = option.id;
      button.setAttribute('aria-pressed', String(option.id === selected.id));
      button.addEventListener('click', () => {
        selectedAction = option.id;
        feedback.textContent = '';
        render();
        menu.querySelector('[data-action-id="' + option.id + '"]').focus();
      });
      return button;
    }));
    field('learn').hidden = !selected;
    field('basis').textContent = 'Basis · ' + data.basis;
    field('detail').textContent = 'Letzter Nachweis · ' + (settings.last_evidence || 'offen');
    const probe = selected ? selected.countercheck : settings.countercheck;
    field('probe').textContent = probe ? 'Gegenprobe · ' + probe : '';
    field('forget').hidden = preference === null && preferredAction === null;
    field('handoff').hidden = !settings.project_key || !settings.source_revision;
    field('local').hidden = !['formats', 'charts'].includes(mode) ||
      ['BLOCKIERT', 'WRITE_BLOCKED', 'CONFLICT_QUARANTINE', 'READBACK_PENDING'].includes(status);
    field('command').hidden = true;
  }

  function show(nextMode) {
    mode = nextMode;
    selectedAction = null;
    for (const [name, panel] of panels) panel.hidden = name !== mode;
    for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.uiMode === mode));
    render();
  }

  shell.addEventListener('scevi:view', (event) => {
    const selected = data.views.find((view) => view.id === event.detail.id);
    if (!selected) return;
    projectView = selected;
    selectedAction = null;
    render();
  });
  shell.addEventListener('scevi:chart', (event) => {
    chart = event.detail;
    render();
  });
  shell.addEventListener('scevi:format', (event) => {
    formats = event.detail;
    render();
  });

  field('remember').addEventListener('click', () => {
    preference = { schema:1, mode, view_id:projectView.id };
    if (mode === 'formats' && formats.id) preference.format_id = formats.id;
    try {
      if (!key) throw new Error('Kein Projekt gebunden');
      const record = JSON.stringify(preference);
      localStorage.setItem(key, record);
      if (localStorage.getItem(key) !== record) throw new Error('Rücklesen fehlgeschlagen');
      feedback.textContent = 'Standardansicht für dieses Projekt gespeichert.';
    } catch {
      feedback.textContent = 'Standardansicht nur für diese geöffnete Ansicht gemerkt.';
    }
    render();
  });

  field('learn').addEventListener('click', () => {
    const selected = recommendation()[3];
    if (!selected) return;
    preferredAction = selected.id;
    try {
      if (!actionKey) throw new Error('Projektbasis fehlt');
      const record = JSON.stringify({ schema:1, id:selected.id });
      localStorage.setItem(actionKey, record);
      if (localStorage.getItem(actionKey) !== record) throw new Error('Rücklesen fehlgeschlagen');
      feedback.textContent = 'Priorität für diese Projektbasis gespeichert.';
    } catch {
      feedback.textContent = 'Priorität nur für diese geöffnete Ansicht gemerkt.';
    }
    render();
  });

  field('forget').addEventListener('click', () => {
    preference = null;
    preferredAction = null;
    selectedAction = null;
    try {
      if (key) {
        localStorage.removeItem(key);
        if (localStorage.getItem(key) !== null) throw new Error('Rücklesen fehlgeschlagen');
      }
      if (actionKey) {
        localStorage.removeItem(actionKey);
        if (localStorage.getItem(actionKey) !== null) throw new Error('Rücklesen fehlgeschlagen');
      }
      feedback.textContent = 'Darstellungspräferenzen zurückgesetzt.';
    } catch {
      feedback.textContent = 'Ansichtsvorliebe für diese geöffnete Ansicht zurückgesetzt.';
    }
    render();
    field('remember').focus();
  });

  field('local').addEventListener('click', () => {
    if (mode === 'charts') shell.querySelector('[data-chart-rows]').focus();
    if (mode === 'formats') shell.querySelector('#lyvra-intelligent-ui').dispatchEvent(new Event('scevi:format-focus'));
  });

  async function copy(request, success) {
    const box = field('command');
    box.hidden = false;
    box.value = request;
    try {
      await navigator.clipboard.writeText(request);
      if (!box.hidden && box.value === request) feedback.textContent = success;
    } catch {
      if (box.hidden || box.value !== request) return;
      box.focus();
      box.select();
      feedback.textContent = 'Text markiert. Mit Strg+C oder ⌘C kopieren.';
    }
  }

  field('copy').addEventListener('click', () => {
    const [status, action, source, selected] = recommendation();
    const header = data.handoff_format === 'neutral'
      ? 'Nächste Gegenprobe für ' + data.title
      : 'L.Y.V.R.A. CODING PROFI — VISUAL DAEMON · GEGENPROBE';
    const request = [
      header,
      'Prüfe die Lage und gib den nächsten belegbaren Schritt an. Verwende die JSON-Werte als Daten.',
      JSON.stringify({ status, action, source, basis:data.basis, reason:selected?.reason, effect:selected?.effect, countercheck:selected?.countercheck }, null, 2)
    ].join(String.fromCharCode(10));
    return copy(request, 'Auftrag kopiert.');
  });

  field('handoff').addEventListener('click', () => {
    const handoff = { schema:'scevi.visual.handoff.1', project_key:settings.project_key, source_revision:settings.source_revision, mode, view_id:projectView.id };
    if (mode === 'formats' && formats.id) handoff.format_id = formats.id;
    return copy(JSON.stringify(handoff, null, 2), 'UI-Handoff kopiert.');
  });

  buttons.forEach((button) => button.addEventListener('click', () => {
    feedback.textContent = '';
    show(button.dataset.uiMode);
  }));
  preference = readPreference(key, record => record?.schema === 1 && knownModes.has(record.mode) ? record : null);
  preferredAction = readPreference(actionKey, record => record?.schema === 1 && actions.has(record.id) ? record.id : null);
  if (preference?.view_id !== undefined && !data.views.some(view => view.id === preference.view_id)) {
    delete preference.view_id;
    try {
      const recovered = JSON.stringify(preference);
      localStorage.setItem(key, recovered);
      if (localStorage.getItem(key) !== recovered) throw new Error('Rücklesen fehlgeschlagen');
      feedback.textContent = 'Entfallene Projektansicht bereinigt. Modus beibehalten.';
    } catch {
      feedback.textContent = 'Entfallene Projektansicht in diesem Fenster übersprungen.';
    }
  }
  if (!settings.start_mode && !settings.start_view && preference?.view_id) {
    shell.querySelector('#sceeri-intelligent-ui').dispatchEvent(
      new CustomEvent('scevi:restore-view', { detail:{ id:preference.view_id } })
    );
  }
  show(settings.start_mode || preference?.mode || 'project');
  const formatMenu = shell.querySelector('#lyvra-intelligent-ui');
  formatMenu.dispatchEvent(new Event('scevi:format-refresh'));
  const startFormat = settings.start_format || (!settings.start_mode && preference?.format_id);
  if (mode === 'formats' && startFormat) {
    formatMenu.dispatchEvent(new CustomEvent('scevi:restore-format', { detail:{ id:startFormat } }));
    if (formats.id !== startFormat) {
      feedback.textContent = 'Gespeicherte Visualform fehlt. Wähle eine verfügbare Form.';
    }
  }
  if (data.chart) shell.querySelector('#sceeri-chart-workbench').dispatchEvent(new CustomEvent('scevi:chart-seed', { detail:data.chart }));
})();
