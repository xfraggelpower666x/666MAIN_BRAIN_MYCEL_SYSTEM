"""FFmpeg encoder command builder shared by Resin 3 output adapters."""


def mp3_command(ffmpeg, samplerate, channels, bitrate):
    return [
        ffmpeg, "-hide_banner", "-nostdin", "-nostats",
        "-probesize", "32", "-analyzeduration", "0", "-fflags", "nobuffer",
        "-f", "s16le", "-ar", str(int(samplerate)), "-ac", str(int(channels)), "-i", "pipe:0",
        "-af", "alimiter=limit=0.9:attack=5:release=60:level=false,ebur128=framelog=info",
        "-c:a", "libmp3lame", "-b:a", f"{int(bitrate)}k",
        "-write_xing", "0", "-id3v2_version", "0", "-flush_packets", "1",
        "-f", "mp3", "pipe:1",
    ]
