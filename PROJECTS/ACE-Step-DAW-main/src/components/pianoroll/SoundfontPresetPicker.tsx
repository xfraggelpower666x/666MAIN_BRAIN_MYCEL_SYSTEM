import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useProjectStore } from '../../store/projectStore';
import type { SoundfontTrackInstrument, TrackInstrument } from '../../types/project';
import {
  deleteSoundbank,
  importSoundbank,
  listSoundbanks,
  SOUNDBANK_CATALOG,
  type SoundbankMetadata,
  type SoundbankPreset,
} from '../../services/soundbankLibrary';

interface SoundfontPresetPickerProps {
  trackId: string;
  currentInstrument?: TrackInstrument;
}

function isSoundfontInstrument(
  instrument: TrackInstrument | undefined,
): instrument is SoundfontTrackInstrument {
  return instrument?.kind === 'soundfont';
}

function presetKey(preset: SoundbankPreset, index: number): string {
  return `${preset.bank}:${preset.bankLsb}:${preset.program}:${index}`;
}

export function SoundfontPresetPicker({ trackId, currentInstrument }: SoundfontPresetPickerProps) {
  const [banks, setBanks] = useState<SoundbankMetadata[]>([]);
  const [selectedBankId, setSelectedBankId] = useState('');
  const [selectedPresetKey, setSelectedPresetKey] = useState('');
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const setTrackInstrument = useProjectStore((state) => state.setTrackInstrument);
  const project = useProjectStore((state) => state.project);

  const refreshBanks = useCallback(async () => {
    const storedBanks = await listSoundbanks();
    setBanks(storedBanks);
    return storedBanks;
  }, []);

  useEffect(() => {
    void refreshBanks().catch((loadError: unknown) => {
      setError(loadError instanceof Error ? loadError.message : 'Could not load local sound banks.');
    }).finally(() => setLoading(false));
  }, [refreshBanks]);

  useEffect(() => {
    if (isSoundfontInstrument(currentInstrument)) {
      setSelectedBankId(currentInstrument.settings.soundBankId);
      setSelectedPresetKey('');
    }
  }, [currentInstrument]);

  useEffect(() => {
    if (loading) return;
    setSelectedBankId((currentId) => (
      banks.some((bank) => bank.id === currentId) ? currentId : banks[0]?.id ?? ''
    ));
  }, [banks, loading]);

  const selectedBank = banks.find((bank) => bank.id === selectedBankId);
  const activeBankMissing = isSoundfontInstrument(currentInstrument)
    && !banks.some((bank) => bank.id === currentInstrument.settings.soundBankId);
  const currentPresetIndex = selectedBank && isSoundfontInstrument(currentInstrument)
    && currentInstrument.settings.soundBankId === selectedBank.id
    ? selectedBank.presets.findIndex((preset) => (
        preset.bank === currentInstrument.settings.bank
        && preset.bankLsb === currentInstrument.settings.bankLsb
        && preset.program === currentInstrument.settings.program
      ))
    : -1;
  const effectivePresetKey = selectedPresetKey || (
    selectedBank && currentPresetIndex >= 0
      ? presetKey(selectedBank.presets[currentPresetIndex]!, currentPresetIndex)
      : ''
  );
  const selectedPreset = useMemo(() => {
    if (!selectedBank || !effectivePresetKey) return undefined;
    const index = Number(effectivePresetKey.slice(effectivePresetKey.lastIndexOf(':') + 1));
    return Number.isInteger(index) && index >= 0 ? selectedBank.presets[index] : undefined;
  }, [effectivePresetKey, selectedBank]);

  const handleFile = async (file?: File) => {
    if (!file) return;
    setBusy(true);
    setError('');
    try {
      const imported = await importSoundbank(file);
      const firstPreset = imported.presets[0];
      if (!firstPreset) throw new Error('The imported sound bank has no playable presets.');
      const storedBanks = await refreshBanks();
      setSelectedBankId(imported.id);
      setSelectedPresetKey(presetKey(firstPreset, 0));
      setBanks(storedBanks);
    } catch (importError) {
      setError(importError instanceof Error ? importError.message : 'Could not import this sound bank.');
    } finally {
      setBusy(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (bank: SoundbankMetadata) => {
    const referenced = project?.tracks.some((track) => (
      isSoundfontInstrument(track.instrument)
      && track.instrument.settings.soundBankId === bank.id
    ));
    if (referenced) {
      setError('This sound bank is assigned to a project track. Change that track instrument before removing it.');
      return;
    }

    setBusy(true);
    setError('');
    try {
      await deleteSoundbank(bank.id);
      const remaining = await refreshBanks();
      if (selectedBankId === bank.id) {
        setSelectedBankId(remaining[0]?.id ?? '');
        setSelectedPresetKey('');
      }
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : 'Could not remove this sound bank.');
    } finally {
      setBusy(false);
    }
  };

  const applyPreset = () => {
    if (!selectedBank || !selectedPreset) return;
    setTrackInstrument(trackId, {
      kind: 'soundfont',
      preset: 'soundfont',
      name: selectedPreset.name,
      settings: {
        soundBankId: selectedBank.id,
        soundBankName: selectedBank.name,
        bankOffset: selectedBank.bankOffset,
        bank: selectedPreset.bank,
        bankLsb: selectedPreset.bankLsb,
        program: selectedPreset.program,
      },
    });
  };

  return (
    <details className="relative">
      <summary className="list-none cursor-pointer px-2 py-1 rounded text-[10px] text-zinc-300 bg-white/5 hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-400">
        SoundFont{isSoundfontInstrument(currentInstrument) ? ` · ${currentInstrument.name}` : ''}
      </summary>
      <div className="absolute right-0 top-full z-[100] mt-2 w-[min(28rem,calc(100vw-2rem))] max-h-[min(70vh,36rem)] overflow-y-auto rounded border border-[#3b3b44] bg-[#1a1a1e] p-3 text-xs text-zinc-200 shadow-xl">
        <div className="flex items-center justify-between gap-3">
          <h2 className="font-medium text-zinc-100">Local SoundFonts</h2>
          <button
            type="button"
            className="rounded bg-violet-600/70 px-2 py-1 text-[10px] text-white hover:bg-violet-600 disabled:cursor-wait disabled:opacity-50"
            disabled={busy}
            onClick={() => fileInputRef.current?.click()}
          >
            {busy ? 'Working…' : 'Import SF2 / SF3 / DLS'}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".sf2,.sf3,.dls"
            className="sr-only"
            aria-label="Import a local SF2, SF3, or DLS sound bank"
            onChange={(event) => void handleFile(event.currentTarget.files?.[0])}
          />
        </div>
        <p className="mt-2 text-[11px] leading-4 text-zinc-300">
          Files stay in this browser&apos;s local storage. The app does not download or bundle third-party banks.
          Import only files you are licensed to use; licenses are not verified.
        </p>
        {activeBankMissing && (
          <p role="alert" className="mt-2 rounded bg-amber-950/60 p-2 text-[11px] leading-4 text-amber-100">
            {currentInstrument.name} refers to a bank that is not stored on this device. Reimport the bank or choose another preset.
          </p>
        )}

        <div className="mt-3 border-t border-[#333] pt-3">
          <h3 className="font-medium text-zinc-200">Catalog</h3>
          <ul className="mt-2 space-y-2">
            {SOUNDBANK_CATALOG.map((item) => (
              <li key={item.name} className="text-[11px] leading-4">
                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-violet-300 underline decoration-violet-500/50 underline-offset-2 hover:text-violet-200"
                >
                  {item.name}
                </a>
                <span className="text-zinc-300"> · {item.format} · </span>
                <a
                  href={item.licenseUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="text-zinc-300 underline decoration-zinc-500 underline-offset-2 hover:text-zinc-100"
                >
                  {item.license}
                </a>
                <p className="text-zinc-400">{item.description}</p>
              </li>
            ))}
          </ul>
        </div>

        {loading ? (
          <div
            className="mt-3 space-y-2 border-t border-[#333] pt-3"
            role="status"
            aria-live="polite"
            aria-label="Loading local sound banks"
          >
            <div className="h-3 w-2/5 animate-pulse rounded bg-white/10" />
            <div className="h-8 w-full animate-pulse rounded bg-white/10" />
          </div>
        ) : banks.length > 0 ? (
          <div className="mt-3 border-t border-[#333] pt-3">
            <label className="block text-[11px] text-zinc-300" htmlFor={`soundfont-bank-${trackId}`}>
              Imported bank
            </label>
            <select
              id={`soundfont-bank-${trackId}`}
              className="mt-1 w-full rounded border border-[#444] bg-[#111] px-2 py-1.5 text-[11px] text-zinc-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-400"
              value={selectedBankId}
              onChange={(event) => {
                setSelectedBankId(event.target.value);
                setSelectedPresetKey('');
              }}
            >
              {banks.map((bank) => (
                <option key={bank.id} value={bank.id}>
                  {bank.name} ({bank.format.toUpperCase()}, {bank.presets.length} presets)
                </option>
              ))}
            </select>

            {selectedBank && (
              <>
                <label className="mt-2 block text-[11px] text-zinc-300" htmlFor={`soundfont-preset-${trackId}`}>
                  Preset
                </label>
                <select
                  id={`soundfont-preset-${trackId}`}
                  className="mt-1 w-full rounded border border-[#444] bg-[#111] px-2 py-1.5 text-[11px] text-zinc-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-400"
                  value={effectivePresetKey}
                  onChange={(event) => setSelectedPresetKey(event.target.value)}
                >
                  <option value="" disabled>Select a preset</option>
                  {selectedBank.presets.map((preset, index) => (
                    <option key={presetKey(preset, index)} value={presetKey(preset, index)}>
                      {preset.name} · bank {preset.bank}/{preset.bankLsb}, program {preset.program + 1}
                    </option>
                  ))}
                </select>
                <div className="mt-2 flex items-center justify-between gap-2">
                  <button
                    type="button"
                    className="rounded bg-violet-600/70 px-2 py-1.5 text-[11px] text-white hover:bg-violet-600 disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={!selectedPreset || busy}
                    onClick={applyPreset}
                  >
                    Use on this track
                  </button>
                  <button
                    type="button"
                    className="rounded px-2 py-1.5 text-[11px] text-red-300 hover:bg-red-950/50 disabled:cursor-not-allowed disabled:opacity-50"
                    disabled={busy}
                    onClick={() => void handleDelete(selectedBank)}
                  >
                    Remove bank
                  </button>
                </div>
              </>
            )}
          </div>
        ) : (
          <p className="mt-3 border-t border-[#333] pt-3 text-[11px] text-zinc-300">
            No sound banks imported yet. Choose a licensed file to add its presets to this track.
          </p>
        )}

        {error && (
          <p role="alert" className="mt-3 rounded bg-red-950/60 p-2 text-[11px] leading-4 text-red-200">
            {error}
          </p>
        )}
      </div>
    </details>
  );
}
