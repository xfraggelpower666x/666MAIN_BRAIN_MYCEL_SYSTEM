'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { test, after } = require('node:test');
const { runInNewContext } = require('node:vm');
const { createAudioLibrary, LIMITS } = require('../src/shared/audio-library.cjs');

const fixtures = path.join(__dirname, 'audio-library-fixtures-' + crypto.randomUUID());
fs.mkdirSync(fixtures);
after(() => fs.rmSync(fixtures, { recursive: true, force: true }));
function dir(name) { const result = path.join(fixtures, name); fs.mkdirSync(result); return result; }
function file(folder, name) { const result = path.join(folder, name); fs.writeFileSync(result, 'not media'); return result; }

test('selected folder scans and rescans; playlists persist, retain missing files and never delete audio', async () => {
  const data = dir('state');
  const music = dir('music');
  const nested = path.join(music, 'nested');
  fs.mkdirSync(nested);
  const one = file(music, 'one.MP3');
  const two = file(nested, 'two.wav');
  file(music, 'ignored.txt');
  const library = createAudioLibrary({ userData: data });
  await library.refresh();
  assert.deepEqual(library.state().pool, []);
  await library.selectFolder(music);
  let state = library.create('Road trip');
  const id = state.playlists[0].id;
  assert.deepEqual(state.pool.map(p => p.name), ['nested' + path.sep + 'two.wav', 'one.MP3']);
  const added = library.addPool(id, state.pool.map(p => p.id));
  assert.equal(added.state.playlists[0].tracks.length, 2);
  library.addFiles(id, [one, path.join(music, 'absent.mp3')]);
  assert.equal(library.state().playlists[0].tracks.length, 2);
  library.rename(id, 'Evening');
  fs.unlinkSync(two);
  const three = file(music, 'three.ogg');
  await library.refresh();
  assert.deepEqual(library.state().pool.map(p => p.name), ['one.MP3', 'three.ogg']);
  const restored = createAudioLibrary({ userData: data });
  assert.equal(restored.state().folder, music);
  assert.equal(restored.state().playlists[0].name, 'Evening');
  assert.equal(restored.state().playlists[0].tracks.filter(p => !p.available).length, 1);
  assert.deepEqual(restored.playlistPaths(id), { paths: [one], missing: 1 });
  await restored.refresh();
  assert.equal(restored.state().pool.length, 2);
  restored.clearFolder();
  await restored.refresh();
  assert.equal(restored.state().folder, '');
  assert.equal(restored.state().pool.length, 0);
  assert.equal(restored.state().playlists.length, 1);
  assert.equal(createAudioLibrary({ userData: data }).state().folder, '');
  restored.removeTrack(id, restored.state().playlists[0].tracks[0].id);
  restored.delete(id);
  assert.ok(fs.existsSync(one) && fs.existsSync(three));
});

test('folder links are skipped and missing folders and read errors are reported', async () => {
  const data = dir('errors-state');
  const music = dir('errors-music');
  const outside = dir('outside');
  const denied = path.join(music, 'denied');
  fs.mkdirSync(denied);
  file(music, 'ok.mp3');
  file(denied, 'hidden.mp3');
  file(outside, 'outside.mp3');
  fs.symlinkSync(outside, path.join(music, 'link'), process.platform === 'win32' ? 'junction' : 'dir');
  const filesystem = {
    ...fs,
    promises: {
      ...fs.promises,
      async opendir(value) {
        if (value === denied) throw Object.assign(new Error('permission denied'), { code: 'EACCES' });
        return fs.promises.opendir(value);
      }
    }
  };
  const library = createAudioLibrary({ userData: data, filesystem });
  await library.selectFolder(music);
  assert.deepEqual(library.state().pool.map(p => p.name), ['ok.mp3']);
  assert.match(library.state().errors.join(' '), /permission denied/);
  await library.selectFolder(path.join(fixtures, 'missing'));
  assert.equal(library.state().pool.length, 0);
  assert.match(library.state().errors.join(' '), /Selected folder/);
  await library.selectFolder(path.join(music, 'link'));
  assert.match(library.state().errors.join(' '), /links are not followed/);
});

test('replacing a scanned directory with a link cannot redirect playlist tracks', async () => {
  const data = dir('swap-state');
  const music = dir('swap-music');
  const outside = dir('swap-outside');
  const sub = path.join(music, 'sub');
  fs.mkdirSync(sub);
  file(sub, 'track.mp3');
  file(outside, 'track.mp3');
  const library = createAudioLibrary({ userData: data });
  await library.selectFolder(music);
  const state = library.create('Safe');
  const id = state.playlists[0].id;
  const selected = state.pool[0].id;
  library.addPool(id, [selected]);
  fs.renameSync(sub, path.join(music, 'original'));
  fs.symlinkSync(outside, sub, process.platform === 'win32' ? 'junction' : 'dir');
  assert.equal(library.state().playlists[0].tracks[0].available, false);
  assert.deepEqual(library.playlistPaths(id), { paths: [], missing: 1 });
  assert.equal(library.addPool(id, [selected]).skipped, 1);
});

test('scanner is bounded and reports truncation', async () => {
  const data = dir('bounds-state');
  const music = dir('bounds-music');
  const realLstat = fs.promises.lstat.bind(fs.promises);
  const filesystem = {
    ...fs,
    promises: {
      ...fs.promises,
      async lstat(value) {
        if (path.dirname(value) === music) return { isFile: () => true, isSymbolicLink: () => false };
        return realLstat(value);
      },
      async realpath(value) {
        return path.dirname(value) === music ? value : fs.promises.realpath(value);
      },
      async opendir() {
        return {
          async *[Symbol.asyncIterator]() {
            for (let i = 0; i < LIMITS.pool + 10; i++) yield {
              name: `${i}.mp3`, isFile: () => true, isDirectory: () => false, isSymbolicLink: () => false
            };
          }
        };
      }
    }
  };
  const library = createAudioLibrary({ userData: data, filesystem });
  await library.selectFolder(music);
  assert.equal(library.state().pool.length, LIMITS.pool);
  assert.match(library.state().errors.join(' '), /limit reached/i);
});

test('invalid names, stale IDs, and persistence failures are surfaced without modifying state', () => {
  const data = dir('fail-state');
  const library = createAudioLibrary({ userData: data });
  const state = library.create('First');
  const id = state.playlists[0].id;
  assert.throws(() => library.create(' first '), /already exists/);
  assert.throws(() => library.create(' '), /playlist name/i);
  assert.throws(() => library.addPool(id, ['../../file.mp3']), /Invalid track selection/);
  assert.throws(() => library.playlistPaths('unknown'), /not found/i);
  const failingFs = { ...fs, writeFileSync() { throw new Error('disk full'); } };
  const failing = createAudioLibrary({ userData: data, filesystem: failingFs });
  assert.throws(() => failing.rename(id, 'Changed'), /disk full/);
  assert.equal(failing.state().playlists[0].name, 'First');
  assert.equal(createAudioLibrary({ userData: data }).state().playlists[0].name, 'First');
});

test('a replaced folder cancels an older scan and repeated refreshes coalesce', async () => {
  const data = dir('race-state');
  const first = dir('race-first');
  const second = dir('race-second');
  file(first, 'old.mp3');
  file(second, 'new.mp3');
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  let started;
  const waiting = new Promise(resolve => { started = resolve; });
  const filesystem = {
    ...fs,
    promises: {
      ...fs.promises,
      async opendir(value) {
        if (value === first) { started(); await gate; }
        return fs.promises.opendir(value);
      }
    }
  };
  const library = createAudioLibrary({ userData: data, filesystem });
  const old = library.selectFolder(first);
  await waiting;
  const same = library.refresh();
  assert.equal(same, library.refresh());
  await library.selectFolder(second);
  release();
  await Promise.all([old, same]);
  assert.equal(library.state().folder, second);
  assert.deepEqual(library.state().pool.map(p => p.name), ['new.mp3']);
});

test('preload accepts only native dropped files and exposes no arbitrary path methods', async () => {
  const preload = fs.readFileSync(path.join(__dirname, '..', 'preload.js'), 'utf8');
  let api;
  let drop;
  let capture;
  const calls = [];
  const context = {
    require: () => ({
      contextBridge: { exposeInMainWorld(_name, value) { api = value; } },
      ipcRenderer: { invoke(channel, ...args) { calls.push([channel, ...args]); return Promise.resolve({ count: 1 }); }, on() {} },
      webUtils: { getPathForFile(file) { return file.nativePath || ''; } }
    }),
    window: { addEventListener(name, fn, useCapture) { if (name === 'drop') { drop = fn; capture = useCapture; } } }
  };
  runInNewContext(preload, context);
  assert.equal(capture, true);
  assert.equal(api.localQueueAddPaths, undefined);
  assert.equal(api.getPathForFile, undefined);
  let result;
  api.onLocalFilesDropped(state => { result = state; });
  const event = { isTrusted: false, target: { closest: () => true }, dataTransfer: { files: [{ nativePath: 'selected.mp3' }] } };
  drop(event);
  assert.equal(calls.length, 0);
  event.isTrusted = true;
  drop(event);
  await Promise.resolve();
  assert.equal(calls[0][0], 'local:queue-add-paths');
  assert.equal(calls[0][1][0], 'selected.mp3');
  assert.equal(result.count, 1);
});

test('large detachable library pages stay bounded and retain selections across filters', async () => {
  const source = fs.readFileSync(path.join(__dirname, '..', 'src', 'app.js'), 'utf8');
  const start = source.indexOf('function setupLocalLibrary(){');
  const end = source.indexOf('\nfunction init()', start);
  assert.ok(start >= 0 && end > start);
  class Element {
    constructor(id = '') { this.id = id; this.value = ''; this.dataset = {}; this.children = []; this.handlers = {}; }
    addEventListener(type, fn) { this.handlers[type] = fn; }
    append(...items) { items.forEach(item => this.appendChild(item)); }
    appendChild(item) { this.children.push(item); if (this.id === 'local-playlist-select' && this.children.length === 1) this.value = item.value; }
    replaceChildren() { this.children = []; if (this.id === 'local-playlist-select') this.value = ''; }
  }
  const elements = new Map();
  const get = id => { if (!elements.has(id)) elements.set(id, new Element(id)); return elements.get(id); };
  let library = { folder: 'chosen', scanning: false, errors: [], pool: Array.from({ length: 2000 }, (_, i) => ({ id: 'track' + i, name: `song${i}.mp3` })), playlists: [] };
  let added;
  let loads = 0;
  const api = {
    onLocalLibraryChanged() {},
    localLibraryState: async () => library,
    localPlaylistCreate: async name => {
      library = { ...library, playlists: [{ id: 'playlist', name, tracks: [] }] };
      return library;
    },
    localPlaylistAddPool: async (id, ids) => {
      added = { id, ids: Array.from(ids) };
      library = { ...library, playlists: [{ id, name: 'Road', tracks: Array.from({ length: 500 }, (_, i) => ({ id: 'track' + i, name: `song${i}.mp3`, available: true })) }] };
      return { state: library, skipped: 0 };
    },
    localPlaylistAddQueue: async () => ({ state: { count: 1, mediaUrl: 'swmedia://audio/current' }, missing: 0 })
  };
  const context = {
    document: { getElementById: get, createElement: () => new Element(), body: { classList: { contains: () => false } } },
    window: { api, confirm: () => true },
    localQueueSnapshot: { count: 0 },
    renderLocalQueue(state) { context.localQueueSnapshot = state; },
    audioElement: { load() { loads++; } }
  };
  runInNewContext(source.slice(start, end), context);
  context.setupLocalLibrary();
  await Promise.resolve();
  get('local-playlist-name').value = 'Road';
  await get('local-playlist-create').handlers.click();
  assert.equal(get('local-pool-list').children.length, 40);
  get('local-pool-list').handlers.change({ target: { dataset: { trackId: 'track0' }, checked: true } });
  get('local-pool-page-next').handlers.click();
  assert.equal(get('local-pool-list').children.length, 40);
  get('local-pool-list').handlers.change({ target: { dataset: { trackId: 'track40' }, checked: true } });
  get('local-pool-filter').value = 'song0.';
  get('local-pool-filter').handlers.input();
  assert.equal(get('local-pool-list').children.length, 1);
  assert.match(get('local-pool-page').textContent, /2 checked/);
  await get('local-pool-add').handlers.click();
  assert.deepEqual(added, { id: 'playlist', ids: ['track0', 'track40'] });
  assert.equal(get('local-playlist-tracks').children.length, 40);
  get('local-playlist-page-next').handlers.click();
  assert.equal(get('local-playlist-tracks').children.length, 40);
  assert.match(get('local-playlist-page').textContent, /Page 2\/13/);
  await get('local-playlist-queue').handlers.click();
  assert.equal(context.localQueueSnapshot.count, 1);
  assert.equal(loads, 0);
  assert.match(get('local-library-status').textContent, /source are preserved/);
});
