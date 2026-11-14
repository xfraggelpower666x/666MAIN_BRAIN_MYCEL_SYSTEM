import { describe, expect, it } from 'vitest';
import {
  findBankOffset,
  importSoundbank,
  MAX_SOUNDBANK_SIZE_BYTES,
} from '../soundbankLibrary';

describe('soundbankLibrary', () => {
  it('allocates non-overlapping MIDI bank ranges within the 7-bit bank limit', () => {
    expect(findBankOffset([{ bankOffset: 0, bankSpan: 4 }], 3)).toBe(4);
    expect(findBankOffset([{ bankOffset: 8, bankSpan: 4 }], 4)).toBe(0);
    expect(() => findBankOffset([{ bankOffset: 0, bankSpan: 128 }], 1))
      .toThrow('There is no free MIDI bank range');
    expect(() => findBankOffset([], 129)).toThrow('invalid MIDI bank range');
  });

  it('rejects unsupported and oversized files before parsing', async () => {
    await expect(importSoundbank(new File(['x'], 'notes.mid')))
      .rejects.toThrow('Choose an SF2, SF3, or DLS sound bank file.');

    const oversized = new File([new Uint8Array(1)], 'bank.sf2');
    Object.defineProperty(oversized, 'size', { value: MAX_SOUNDBANK_SIZE_BYTES + 1 });
    await expect(importSoundbank(oversized)).rejects.toThrow('Sound bank files must be between');
  });
});
