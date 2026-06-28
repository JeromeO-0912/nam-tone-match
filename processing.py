import json
import numpy as np
import librosa

SR = 22050 # RESAMPLE_RATE

# FREQ BANDS (HZ) - like a coarse graphic EQ. Top band stops near Nyquist (SR/2).
BANDS = [
    ("sub",        20,   60),
    ("low",        60,   250),
    ("low_mid",    250,  500),
    ("mid",        500,  2000),
    ("high_mid",   2000, 4000),
    ("presence",   4000, 6000),
    ("brilliance", 6000, 11000),
]

def load_audio(path):
    # mono +  resample to SR
    audio, _ = librosa.load(path, sr=SR, mono=True)
    # RMS-normalize otherwise a louder clips look likea broadband boost in the EQ
    rms = np.sqrt(np.mean(audio**2))
    if rms > 0:
        audio = audio / rms
    return audio

def band_levels(y, n_fft=2048):
    # Average magnitude spectrum across the whole clip
    spectrum = np.abs(librosa.stft(y, n_fft=n_fft))
    avg_spectrum = np.mean(spectrum, axis=1)
    frequencies = librosa.fft_frequencies(sr=SR, n_fft=n_fft)

    levels = {}
    for name, lo, hi in BANDS:
        mask = (frequencies >= lo) & (frequencies < hi)
        band_mag = np.mean(avg_spectrum[mask])
        levels[name] = float(20 * np.log(band_mag + 1e-9))  # Convert to dB, avoid log(0)

    return levels

def run_tone_match(di_path, reference_path, output_path):
    di_audio = load_audio(di_path)
    reference_audio = load_audio(reference_path)

    di_levels = band_levels(di_audio)
    reference_levels = band_levels(reference_audio)

    # EQ MATCH
    diff = {name: reference_levels[name] - di_levels[name] for name, _, _ in BANDS}

    # CENTER THE CURVE FOR TONAL SHAPE NOT OVERALL GAIN
    mean_offset = sum(diff.values()) / len(diff)
    eq_curve = {name: diff[name] - mean_offset for name in diff}

    # BRIGHTNESS
    di_brightness = float(np.mean(librosa.feature.spectral_centroid(y=di_audio, sr=SR)))
    reference_brightness = float(np.mean(librosa.feature.spectral_centroid(y=reference_audio, sr=SR)))

    result = {
        "eq_match_db": eq_curve,
        "di_brightness_hz": round(di_brightness, 2),
        "reference_brightness_hz": round(reference_brightness, 2),
        "bands_hz": {name: [lo, hi] for name, lo, hi in BANDS},
        "note": "eq_match_db is the difference in dB between the reference and DI for each frequency band. Positive values mean the reference is louder in that band.",
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=4)
    return output_path

