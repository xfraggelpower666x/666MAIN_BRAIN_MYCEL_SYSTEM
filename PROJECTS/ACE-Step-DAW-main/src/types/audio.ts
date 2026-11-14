export interface ClipPlaybackInfo {
  clipId: string;
  trackId: string;
  startTime: number;
  duration: number;
  audioBuffer: AudioBuffer | null;
}

export interface TrackRouting {
  trackId: string;
  gainNode: GainNode;
  volume: number;
  muted: boolean;
  soloed: boolean;
}
