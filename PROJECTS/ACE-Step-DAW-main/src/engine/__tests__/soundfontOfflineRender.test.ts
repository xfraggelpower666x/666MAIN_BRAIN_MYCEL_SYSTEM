import { BasicMIDI } from 'spessasynth_core';
import { describe, expect, it } from 'vitest';
import type { MidiNote, SoundfontTrackInstrument } from '../../types/project';
import { buildSoundfontMidiBuffer } from '../soundfontOfflineRender';

const instrument: SoundfontTrackInstrument = {
  kind: 'soundfont',
  preset: 'soundfont',
  name: 'Cello',
  settings: {
    soundBankId: 'local-bank',
    soundBankName: 'Orchestra',
    bankOffset: 4,
    bank: 2,
    bankLsb: 1,
    program: 42,
  },
};

describe('buildSoundfontMidiBuffer', () => {
  it('creates a playable MIDI sequence with bank, program, and note events', () => {
    const notes: MidiNote[] = [
      { pitch: 60, velocity: 0.8, startBeat: 1, durationBeats: 2 },
    ];

    const midi = BasicMIDI.fromArrayBuffer(
      buildSoundfontMidiBuffer(notes, 0, 120, 4, instrument),
    );
    const events = midi.tracks[0]?.events ?? [];

    expect(midi.timeDivision).toBe(480);
    expect(events.some((event) => event.statusByte === 0xb0 && event.data[0] === 0)).toBe(true);
    expect(events.some((event) => event.statusByte === 0xc0 && event.data[0] === 42)).toBe(true);
    expect(events.some((event) => event.statusByte === 0x90 && event.data[0] === 60)).toBe(true);
    expect(events.some((event) => event.statusByte === 0x80 && event.data[0] === 60)).toBe(true);
  });

  it('clips notes at the render boundaries and rejects invalid tempo', () => {
    const midi = BasicMIDI.fromArrayBuffer(buildSoundfontMidiBuffer([
      { pitch: 60, velocity: 0.5, startBeat: -2, durationBeats: 3 },
      { pitch: 62, velocity: 0.5, startBeat: 8, durationBeats: 1 },
    ], 0, 120, 1, instrument));
    const notes = midi.tracks[0]?.events.filter((event) => event.statusByte === 0x90) ?? [];

    expect(notes).toHaveLength(1);
    expect(() => buildSoundfontMidiBuffer([], 0, 0, 1, instrument)).toThrow('BPM must be greater than zero.');
  });
});
