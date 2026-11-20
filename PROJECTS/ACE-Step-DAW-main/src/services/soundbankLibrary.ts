import { createStore, del, get, keys, set } from 'idb-keyval';

export const MAX_SOUNDBANK_SIZE_BYTES = 512 * 1024 * 1024;
const META_PREFIX = 'meta:';
const DATA_PREFIX = 'data:';
const soundbankStore = createStore('ace-step-soundbank-library', 'soundbanks');

export interface SoundbankPreset {
  name: string;
  bank: number;
  bankLsb: number;
  program: number;
}

export interface SoundbankMetadata {
  id: string;
  name: string;
  fileName: string;
  format: 'sf2' | 'sf3' | 'dls';
  bankOffset: number;
  bankSpan: number;
  presets: SoundbankPreset[];
  importedAt: number;
}

export const SOUNDBANK_CATALOG = [
  {
    name: 'theDAW Orchestra',
    format: 'SF3',
    license: 'CC0 1.0 Universal',
    licenseUrl: 'https://creativecommons.org/publicdomain/zero/1.0/',
    description: 'Orchestral bank; download and import the SF3 yourself.',
    url: 'https://github.com/gantasmo/theDAW/releases?q=soundbank-orchestra',
  },
  {
    name: 'Sonatina Symphonic Orchestra',
    format: 'SF2',
    license: 'Creative Commons Sampling Plus 1.0',
    licenseUrl: 'https://creativecommons.org/licenses/sampling+/1.0/',
    description: 'Download the ZIP, extract an SF2, then import it. The app does not extract archives.',
    url: 'https://archive.org/download/SonatinaSymphonicOrchestraSF2/Sonatina%20Symphonic%20Orchestra%20SF2.zip',
  },
  {
    name: 'Virtual Playing Orchestra 3',
    format: 'SFZ',
    license: 'Mixed CC Sampling Plus / CC BY-SA / CC0',
    licenseUrl: 'https://virtualplaying.com/virtual-playing-orchestra/',
    description: 'SFZ is not supported by this player; files are not imported or bundled.',
    url: 'https://virtualplaying.com/virtual-playing-orchestra/',
  },
] as const;

function metadataKey(id: string): string {
  return `${META_PREFIX}${id}`;
}

function dataKey(id: string): string {
  return `${DATA_PREFIX}${id}`;
}

export function findBankOffset(
  banks: ReadonlyArray<Pick<SoundbankMetadata, 'bankOffset' | 'bankSpan'>>,
  bankSpan: number,
): number {
  if (!Number.isInteger(bankSpan) || bankSpan < 1 || bankSpan > 128) {
    throw new Error('This sound bank has an invalid MIDI bank range.');
  }

  for (let offset = 0; offset + bankSpan <= 128; offset += 1) {
    const overlaps = banks.some((bank) => (
      offset < bank.bankOffset + bank.bankSpan
      && bank.bankOffset < offset + bankSpan
    ));
    if (!overlaps) return offset;
  }

  throw new Error('There is no free MIDI bank range for this sound bank.');
}

export async function listSoundbanks(): Promise<SoundbankMetadata[]> {
  const allKeys = await keys(soundbankStore);
  const metadataKeys = allKeys.filter(
    (key): key is string => typeof key === 'string' && key.startsWith(META_PREFIX),
  );
  const results = await Promise.all(
    metadataKeys.map((key) => get<SoundbankMetadata>(key, soundbankStore)),
  );
  return results
    .filter((entry): entry is SoundbankMetadata => Boolean(entry))
    .sort((a, b) => a.name.localeCompare(b.name));
}

export async function getSoundbankData(id: string): Promise<ArrayBuffer> {
  const data = await get<ArrayBuffer>(dataKey(id), soundbankStore);
  if (!data) throw new Error('The sound bank file is missing from local storage.');
  return data.slice(0);
}

export async function importSoundbank(file: File): Promise<SoundbankMetadata> {
  const extension = file.name.split('.').pop()?.toLowerCase();
  if (extension !== 'sf2' && extension !== 'sf3' && extension !== 'dls') {
    throw new Error('Choose an SF2, SF3, or DLS sound bank file.');
  }
  if (file.size === 0 || file.size > MAX_SOUNDBANK_SIZE_BYTES) {
    throw new Error(`Sound bank files must be between 1 byte and ${MAX_SOUNDBANK_SIZE_BYTES / (1024 * 1024)} MiB.`);
  }

  const buffer = await file.arrayBuffer();
  const { BasicSoundBank, SoundBankLoader } = await import('spessasynth_core');
  await BasicSoundBank.ready;
  const parsed = SoundBankLoader.fromArrayBuffer(buffer, {
    sampleData: false,
    copySampleData: false,
  });
  const presets = parsed.presets.map((preset) => ({
    name: preset.name,
    bank: preset.bankMSB,
    bankLsb: preset.bankLSB,
    program: preset.program,
  }));
  if (presets.length === 0) throw new Error('The selected file contains no playable presets.');

  const bankSpan = presets.reduce((span, preset) => Math.max(span, preset.bank + 1), 1);
  const banks = await listSoundbanks();
  const id = crypto.randomUUID();
  const metadata: SoundbankMetadata = {
    id,
    name: file.name.replace(/\.[^.]+$/, ''),
    fileName: file.name,
    format: extension,
    bankOffset: findBankOffset(banks, bankSpan),
    bankSpan,
    presets,
    importedAt: Date.now(),
  };

  await set(dataKey(id), buffer, soundbankStore);
  try {
    await set(metadataKey(id), metadata, soundbankStore);
  } catch (error) {
    await del(dataKey(id), soundbankStore);
    throw error;
  }
  return metadata;
}

export async function deleteSoundbank(id: string): Promise<void> {
  await del(dataKey(id), soundbankStore);
  await del(metadataKey(id), soundbankStore);
}
