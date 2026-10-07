import numpy as np
from . import wav_reader

def read_wav_histogram(path, bins=256):
    rate, samples = wav_reader.read_wav(path)
    return wav_histogram(samples, bins=bins)


def wav_histogram(samples, bins=256):

    flat = samples.flatten().astype(np.float64)

    if samples.dtype == np.int16:
        flat = flat + 32768.0
        flat = flat / 65535.0 * (bins - 1)
    elif samples.dtype == np.uint8:
        flat = flat / 255.0 * (bins - 1)

    flat = np.clip(np.round(flat), 0, bins - 1).astype(np.int32)
    counts = np.bincount(flat, minlength=bins)

    return counts