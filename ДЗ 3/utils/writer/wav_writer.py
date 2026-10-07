import wave
import numpy as np

def write_wav(path, rate, samples):
    if samples.ndim == 1:
        n_channels = 1
        frames = samples
    else:
        n_channels = samples.shape[1]
        frames = samples

    if frames.dtype != np.int16:
        frames = frames.astype(np.int16)

    with wave.open(path, 'wb') as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(2)          # 16 бит = 2 байта
        wf.setframerate(rate)
        wf.writeframes(frames.tobytes())