import { useState, useEffect } from 'react';
import { getAudioEngine } from './useAudioEngine';
import { loadAudioBlobByKey } from '../services/audioFileManager';
import { computeWaveformPeaks } from '../utils/waveformPeaks';

export function useWaveform(
  audioKey: string | null,
  numPeaks: number = 100,
  startTime: number = 0,
  duration?: number,
) {
  const [peaks, setPeaks] = useState<number[] | null>(null);

  useEffect(() => {
    if (!audioKey) {
      setPeaks(null);
      return;
    }

    let cancelled = false;

    (async () => {
      try {
        const blob = await loadAudioBlobByKey(audioKey);
        if (!blob || cancelled) return;

        const engine = getAudioEngine();
        const buffer = await engine.decodeAudioData(blob);
        if (cancelled) return;

        const sampleRate = buffer.sampleRate;
        const startSample = Math.floor(startTime * sampleRate);
        const endSample = duration != null
          ? Math.min(Math.floor((startTime + duration) * sampleRate), buffer.length)
          : buffer.length;

        const p = computeWaveformPeaks(buffer, numPeaks, startSample, endSample);
        setPeaks(p);
      } catch {
        // Ignore decode errors
      }
    })();

    return () => { cancelled = true; };
  }, [audioKey, numPeaks, startTime, duration]);

  return peaks;
}
