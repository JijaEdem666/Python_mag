import wave

import numpy as np


def read_wav(path):
    with wave.open(path, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()

        raw = wf.readframes(n_frames)

    if sampwidth == 2:
        dtype = np.int16
    elif sampwidth == 1:
        dtype = np.uint8
    elif sampwidth == 4:
        dtype = np.int32
    else:
        raise ValueError(f'Unsupported sample width: {sampwidth}')

    data = np.frombuffer(raw, dtype=dtype)

    if n_channels > 1:
        data = data.reshape(-1, n_channels)

    return framerate, data
