import { BasicMIDI } from 'spessasynth_core';
import { WorkletSynthesizer } from 'spessasynth_lib';
import type { MidiNote, SoundfontTrackInstrument } from '../types/project';
import { getSoundbankData } from '../services/soundbankLibrary';
import { loadSoundfontWorklet } from './soundfontRuntime';

const TICKS_PER_BEAT = 480;

interface MidiEvent {
  tick: number;
  order: number;
  bytes: number[];
}

function encodeVariableLength(value: number): number[] {
  let remaining = Math.max(0, Math.floor(value));
  const bytes = [remaining & 0x7f];
  while ((remaining >>= 7) > 0) bytes.unshift((remaining & 0x7f) | 0x80);
  return bytes;
}

function writeUint32(value: number): number[] {
  return [(value >>> 24) & 0xff, (value >>> 16) & 0xff, (value >>> 8) & 0xff, value & 0xff];
}

function writeUint16(value: number): number[] {
  return [(value >>> 8) & 0xff, value & 0xff];
}

export function buildSoundfontMidiBuffer(
  notes: MidiNote[],
  clipStartTime: number,
  bpm: number,
  totalDuration: number,
  instrument: SoundfontTrackInstrument,
): ArrayBuffer {
  if (!Number.isFinite(bpm) || bpm <= 0) throw new Error('BPM must be greater than zero.');

  const events: MidiEvent[] = [
    { tick: 0, order: -3, bytes: [0xff, 0x51, 0x03, ...writeUint32(Math.round(60_000_000 / bpm)).slice(1)] },
    { tick: 0, order: -2, bytes: [0xb0, 0, instrument.settings.bankOffset + instrument.settings.bank] },
    { tick: 0, order: -1, bytes: [0xb0, 32, instrument.settings.bankLsb] },
    { tick: 0, order: 0, bytes: [0xc0, instrument.settings.program] },
  ];

  for (const note of notes) {
    const duration = Math.max(0, note.durationBeats * 60 / bpm);
    const start = clipStartTime + note.startBeat * 60 / bpm;
    const end = start + duration;
    if (duration <= 0 || end <= 0 || start >= totalDuration) continue;

    const clippedStart = Math.max(0, start);
    const clippedEnd = Math.min(totalDuration, end);
    if (clippedEnd <= clippedStart) continue;
    const startTick = Math.max(0, Math.round(clippedStart * bpm / 60 * TICKS_PER_BEAT));
    const endTick = Math.max(startTick + 1, Math.round(clippedEnd * bpm / 60 * TICKS_PER_BEAT));
    const pitch = Math.max(0, Math.min(127, Math.round(note.pitch)));
    const velocity = Math.max(0, Math.min(127, Math.round(note.velocity * 127)));
    if (velocity === 0) continue;
    events.push(
      { tick: startTick, order: 1, bytes: [0x90, pitch, velocity] },
      { tick: endTick, order: 0, bytes: [0x80, pitch, 0] },
    );
  }

  events.sort((a, b) => a.tick - b.tick || a.order - b.order);
  const trackBytes: number[] = [];
  let previousTick = 0;
  for (const event of events) {
    trackBytes.push(...encodeVariableLength(event.tick - previousTick), ...event.bytes);
    previousTick = event.tick;
  }
  trackBytes.push(0, 0xff, 0x2f, 0);

  const fileBytes = [
    0x4d, 0x54, 0x68, 0x64,
    ...writeUint32(6),
    ...writeUint16(0),
    ...writeUint16(1),
    ...writeUint16(TICKS_PER_BEAT),
    0x4d, 0x54, 0x72, 0x6b,
    ...writeUint32(trackBytes.length),
    ...trackBytes,
  ];
  return new Uint8Array(fileBytes).buffer;
}

export async function renderSoundfontTrackOffline(
  notes: MidiNote[],
  clipStartTime: number,
  bpm: number,
  totalDuration: number,
  sampleRate: number,
  instrument: SoundfontTrackInstrument,
): Promise<AudioBuffer> {
  const midiSequence = BasicMIDI.fromArrayBuffer(
    buildSoundfontMidiBuffer(notes, clipStartTime, bpm, totalDuration, instrument),
  );
  const soundBankBuffer = await getSoundbankData(instrument.settings.soundBankId);
  const length = Math.max(1, Math.ceil(totalDuration * sampleRate));
  const context = new OfflineAudioContext(2, length, sampleRate);
  await loadSoundfontWorklet(context);
  const synth = new WorkletSynthesizer(context, { eventsEnabled: false });
  synth.connect(context.destination);
  await synth.startOfflineRender({
    midiSequence,
    loopCount: 0,
    soundBankList: [{
      bankOffset: instrument.settings.bankOffset,
      soundBankBuffer,
    }],
  });
  await synth.isReady;
  return context.startRendering();
}
