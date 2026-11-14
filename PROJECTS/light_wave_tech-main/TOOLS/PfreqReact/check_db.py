    "The Cosmic Wyrdetide.wav",						# SEMISUPA "story"
    "Instrumental v3.wav",						# SUPAGOOD "glitchy" TOO MUCH SYNC-MOVEMENT



import soundfile as sf
import pyloudnorm as pyln

# 1. Read the audio file
# data is a numpy array, rate is the sample rate (e.g., 44100)

audio_filepath = "C:/Users/micha/Downloads/pier_wank/NORMAL_MM/0 The Nāga Protocol.wav"

data, rate = sf.read(audio_filepath)

# 2. Create a meter to measure loudness
meter = pyln.Meter(rate) # create BS.1770 meter

# 3. Measure integrated (overall) perceived loudness
loudness_lufs = meter.integrated_loudness(data)

print(f"Perceived Loudness: {loudness_lufs:.2f} LUFS")

from pydub import AudioSegment

# Load the wav file
audio = AudioSegment.from_file(audio_filepath, format="wav")

# Average (RMS) Volume relative to Full Scale
average_db = audio.dBFS

# Peak Volume (the single loudest point in the file)
peak_db = audio.max_dBFS

print(f"Average Volume (RMS): {average_db:.2f} dBFS")
print(f"Peak Volume: {peak_db:.2f} dBFS")