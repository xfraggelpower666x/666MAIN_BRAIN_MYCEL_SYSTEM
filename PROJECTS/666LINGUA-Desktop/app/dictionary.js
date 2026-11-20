'use strict';

let dictionaryEntries = [];
let editedTerm;
let dictionaryBusy = false;

function dictionaryStatus(message) {
  el('dictionary-status').textContent = message;
}

function resetDictionaryEditor() {
  editedTerm = undefined;
  el('dictionary-source').readOnly = false;
  el('dictionary-source').value = '';
  el('dictionary-target').value = '';
  el('dictionary-cancel').hidden = true;
}

function renderDictionary() {
  const entries = el('dictionary-entries');
  entries.replaceChildren();
  const search = normalized(el('dictionary-search').value);
  const from = el('dictionary-direction').value;
  const filtered = dictionaryEntries.filter(entry =>
    entry.from === from && [entry.source, entry.target].some(term => normalized(term).includes(search)));
  filtered.sort((a, b) => a.source.localeCompare(b.source, from));
  if (!filtered.length) entries.append(node('p', t('Noch keine passenden Begriffe.'), 'muted'));
  for (const entry of filtered) {
    const row = node('div', undefined, 'dictionary-entry');
    row.append(node('strong', entry.source), node('span', '→', 'dictionary-arrow'), node('span', entry.target));
    const actions = node('div', undefined, 'dictionary-actions');
    const edit = node('button', t('Bearbeiten'), 'quiet');
    const remove = node('button', t('Löschen'), 'quiet');
    edit.type = remove.type = 'button';
    edit.disabled = remove.disabled = dictionaryBusy;
    edit.addEventListener('click', () => {
      editedTerm = entry;
      el('dictionary-source').value = entry.source;
      el('dictionary-source').readOnly = true;
      el('dictionary-target').value = entry.target;
      el('dictionary-cancel').hidden = false;
      el('dictionary-target').focus();
    });
    remove.addEventListener('click', () => deleteDictionaryEntry(entry));
    actions.append(edit, remove);
    row.append(actions);
    entries.append(row);
  }
}

async function loadDictionary() {
  try {
    dictionaryEntries = await api('dictionary');
    renderDictionary();
  } catch (error) {
    dictionaryStatus(error.message);
  }
}

function dictionaryMutating(active) {
  dictionaryBusy = active;
  for (const id of ['dictionary-save','dictionary-cancel','dictionary-direction','dictionary-source','dictionary-target']) el(id).disabled = active;
  renderDictionary();
}

el('dictionary-direction').addEventListener('change', () => {
  resetDictionaryEditor();
  dictionaryStatus('');
  renderDictionary();
});
el('dictionary-search').addEventListener('input', renderDictionary);
el('dictionary-cancel').addEventListener('click', resetDictionaryEditor);
el('dictionary-form').addEventListener('submit', async event => {
  event.preventDefault();
  if (dictionaryBusy) return;
  const from = el('dictionary-direction').value;
  const text = el('dictionary-source').value;
  const target = el('dictionary-target').value;
  dictionaryMutating(true);
  try {
    const previous = editedTerm ? await hash(editedTerm.target) : '';
    const saved = await api('dictionary', {from, to: from === 'de' ? 'en' : 'de', text, target, previous});
    dictionaryEntries = dictionaryEntries.filter(entry => entry.id !== saved.id);
    dictionaryEntries.push(saved);
    resetDictionaryEditor();
    clearResult();
    dictionaryStatus(t('Begriff gespeichert.'));
  } catch (error) {
    dictionaryStatus(error.message);
    await loadDictionary();
  } finally {
    dictionaryMutating(false);
  }
});

async function deleteDictionaryEntry(entry) {
  if (dictionaryBusy || !confirm(t('Diesen Begriff löschen?'))) return;
  dictionaryMutating(true);
  try {
    await api('dictionary/delete', {id: entry.id, previous: await hash(entry.target)});
    dictionaryEntries = dictionaryEntries.filter(item => item.id !== entry.id);
    if (editedTerm?.id === entry.id) resetDictionaryEditor();
    clearResult();
    dictionaryStatus(t('Begriff gelöscht.'));
  } catch (error) {
    dictionaryStatus(error.message);
    await loadDictionary();
  } finally {
    dictionaryMutating(false);
  }
}
