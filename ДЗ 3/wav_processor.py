import numpy as np
from utils.reader import wav_reader
from utils.writer import wav_writer

def process_wav(path, output_path):
    rate, samples = wav_reader.read_wav(path)
    print(f'WAV: rate={rate}, shape={samples.shape}, dtype={samples.dtype}')

    hist = wav_histogram(samples, bins=256)
    print(f'Histogram (256 bins): {hist}')

    quantized_samples, quantized_codes = quantize_audio(samples, levels=256)
    print(f'Unique quantized levels: {np.unique(quantized_codes).size}')

    if output_path:
        wav_writer.write_wav(output_path, rate, quantized_samples)
        print(f'Saved: {output_path}')


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

def quantize_audio(samples, levels=256):

    flat = samples.flatten().astype(np.float64)

    if samples.dtype == np.int16:
        normalized = (flat + 32768.0) / 65535.0
        quantized = np.round(normalized * (levels - 1)).astype(np.int32)

        restored = (quantized / (levels - 1)) * 65535.0 - 32768.0
        restored = np.clip(np.round(restored), -32768, 32767).astype(np.int16)

    elif samples.dtype == np.uint8:
        normalized = flat / 255.0
        quantized = np.round(normalized * (levels - 1)).astype(np.int32)
        restored = np.round((quantized / (levels - 1)) * 255.0).astype(np.uint8)
    else:
        raise ValueError(f'Unsupported dtype for quantization: {samples.dtype}')

    if samples.ndim > 1:
        restored = restored.reshape(samples.shape)

    return restored, quantized