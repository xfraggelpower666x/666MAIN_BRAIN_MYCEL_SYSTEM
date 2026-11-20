import type { WorkletSynthesizer } from 'spessasynth_lib';
import { getSoundbankData } from '../services/soundbankLibrary';
import type { SoundfontTrackInstrument } from '../types/project';
import { createSoundfontSynth } from './soundfontRuntime';

interface SoundfontChannel {
  channel: number;
  output: AudioNode;
}

export class SoundfontEngine {
  private context: BaseAudioContext | null = null;
  private masterOutput: AudioNode | null = null;
  private synth: WorkletSynthesizer | null = null;
  private synthPromise: Promise<WorkletSynthesizer> | null = null;
  private readonly loadedBanks = new Set<string>();
  private readonly bankLoads = new Map<string, Promise<void>>();
  private readonly channels = new Map<string, SoundfontChannel>();
  private readonly usedChannels = new Set<number>();

  async prepareTrack(
    trackId: string,
    instrument: SoundfontTrackInstrument,
    context: BaseAudioContext,
    masterOutput: AudioNode,
    trackOutput: AudioNode,
  ): Promise<void> {
    const synth = await this.getSynth(context, masterOutput);
    await this.loadBank(synth, instrument.settings.soundBankId, instrument.settings.bankOffset);
    const channel = this.channels.get(trackId) ?? this.allocateChannel(trackId, synth, trackOutput);
    this.routeChannel(trackId, channel.channel, trackOutput, synth);

    synth.controllerChange(channel.channel, 0, instrument.settings.bankOffset + instrument.settings.bank);
    synth.controllerChange(channel.channel, 32, instrument.settings.bankLsb);
    synth.programChange(channel.channel, instrument.settings.program);
  }

  triggerAttackRelease(
    trackId: string,
    pitch: number,
    durationSeconds: number,
    velocity: number,
  ): void {
    const synth = this.synth;
    const channel = this.channels.get(trackId);
    if (!synth || !channel) {
      throw new Error('The sound bank instrument has not been prepared for playback.');
    }

    const start = this.context?.currentTime ?? 0;
    const clampedPitch = Math.max(0, Math.min(127, Math.round(pitch)));
    const clampedVelocity = Math.max(0, Math.min(127, Math.round(velocity * 127)));
    if (clampedVelocity === 0) return;
    const noteDuration = Math.max(0.01, durationSeconds);
    synth.noteOn(channel.channel, clampedPitch, clampedVelocity, { time: start });
    synth.noteOff(channel.channel, clampedPitch, { time: start + noteDuration });
  }

  noteOn(trackId: string, pitch: number, velocity: number): void {
    const channel = this.channels.get(trackId);
    if (!this.synth || !channel) throw new Error('The SoundFont track is not ready.');
    const clampedVelocity = Math.max(0, Math.min(127, Math.round(velocity)));
    if (clampedVelocity === 0) return;
    this.synth.noteOn(
      channel.channel,
      Math.max(0, Math.min(127, Math.round(pitch))),
      clampedVelocity,
    );
  }

  noteOff(trackId: string, pitch: number): void {
    const channel = this.channels.get(trackId);
    if (!this.synth || !channel) return;
    this.synth.noteOff(channel.channel, Math.max(0, Math.min(127, Math.round(pitch))));
  }

  releaseAll(): void {
    this.synth?.stopAll(true);
  }

  removeTrack(trackId: string): void {
    const channel = this.channels.get(trackId);
    const synth = this.synth;
    if (!channel || !synth || !this.masterOutput) return;
    synth.controllerChange(channel.channel, 123, 0);
    synth.disconnectChannel(channel.output, channel.channel);
    synth.connectChannel(this.masterOutput, channel.channel);
    this.channels.delete(trackId);
    this.usedChannels.delete(channel.channel);
  }

  resetRouting(): void {
    const synth = this.synth;
    if (!synth || !this.masterOutput) return;
    synth.stopAll(true);
    for (const binding of this.channels.values()) {
      synth.disconnectChannel(binding.output, binding.channel);
      synth.connectChannel(this.masterOutput, binding.channel);
      synth.controllerChange(binding.channel, 123, 0);
    }
    this.channels.clear();
    this.usedChannels.clear();
  }

  private async getSynth(
    context: BaseAudioContext,
    masterOutput: AudioNode,
  ): Promise<WorkletSynthesizer> {
    if (context !== this.context) {
      this.context = context;
      this.masterOutput = masterOutput;
      this.synth = null;
      this.synthPromise = null;
      this.loadedBanks.clear();
      this.bankLoads.clear();
      this.channels.clear();
      this.usedChannels.clear();
    }

    if (!this.synthPromise) {
      this.synthPromise = createSoundfontSynth(context)
        .then((synth) => {
          synth.connect(masterOutput);
          this.synth = synth;
          return synth;
        })
        .catch((error: unknown) => {
          this.synth = null;
          this.synthPromise = null;
          throw error;
        });
    }
    return this.synthPromise;
  }

  private async loadBank(
    synth: WorkletSynthesizer,
    bankId: string,
    bankOffset: number,
  ): Promise<void> {
    if (this.loadedBanks.has(bankId)) return;
    const existing = this.bankLoads.get(bankId);
    if (existing) return existing;

    const load = getSoundbankData(bankId)
      .then((data) => synth.soundBankManager.addSoundBank(data, bankId, bankOffset))
      .then(() => {
        this.loadedBanks.add(bankId);
      })
      .finally(() => {
        this.bankLoads.delete(bankId);
      });
    this.bankLoads.set(bankId, load);
    return load;
  }

  private allocateChannel(
    trackId: string,
    synth: WorkletSynthesizer,
    trackOutput: AudioNode,
  ): SoundfontChannel {
    const channel = Array.from({ length: 16 }, (_, index) => index)
      .find((candidate) => !this.usedChannels.has(candidate));
    if (channel === undefined || !this.masterOutput) {
      throw new Error('All 16 SoundFont MIDI channels are in use.');
    }

    synth.disconnectChannel(this.masterOutput, channel);
    synth.connectChannel(trackOutput, channel);
    const binding = { channel, output: trackOutput };
    this.channels.set(trackId, binding);
    this.usedChannels.add(channel);
    return binding;
  }

  private routeChannel(
    trackId: string,
    channelNumber: number,
    trackOutput: AudioNode,
    synth: WorkletSynthesizer,
  ): void {
    const binding = this.channels.get(trackId);
    if (!binding || binding.channel !== channelNumber || binding.output === trackOutput) return;
    synth.disconnectChannel(binding.output, channelNumber);
    synth.connectChannel(trackOutput, channelNumber);
    binding.output = trackOutput;
  }
}

export const soundfontEngine = new SoundfontEngine();
