import copy

import practice_7_oop_patterns.decoders.decoder
import practice_7_oop_patterns.encoders.encoder

import os

"""
Стратегия (Strategy)
"""

class Hist:


    @classmethod
    def read(cls, file_path):
        ext = file_path.rsplit('.', 1)[-1]
        if ext == 'bin':
            decoder = practice_7_oop_patterns.decoders.decoder.BinHistDecoder
        elif ext == 'txt':
            decoder = practice_7_oop_patterns.decoders.decoder.TxtHistDecoder
        elif ext == 'json':
            decoder = practice_7_oop_patterns.decoders.decoder.JsonHistDecoder
        elif ext == 'csv':
            decoder = practice_7_oop_patterns.decoders.decoder.CsvHistDecoder
        elif ext in ('png', 'jpg', 'jpeg', 'bmp'):
            decoder = practice_7_oop_patterns.decoders.decoder.ImageHistDecoder
        else:
            raise RuntimeError('Невозможно получить данные %s' % file_path)
        data = decoder.decode(file_path)
        return cls(data)

    def write(self, filename):
        ext = filename.rsplit('.', 1)[-1]
        if ext == 'bin':
            encoder = practice_7_oop_patterns.encoders.encoder.BinHistEncoder
        elif ext == 'txt':
            encoder = practice_7_oop_patterns.encoders.encoder.TxtHistEncoder
        elif ext == 'json':
            encoder = practice_7_oop_patterns.encoders.encoder.JsonHistEncoder
        elif ext == 'csv':
            encoder = practice_7_oop_patterns.encoders.encoder.CsvHistEncoder
        elif ext in ('png', 'jpg', 'jpeg', 'bmp'):
            encoder = practice_7_oop_patterns.encoders.encoder.ImageHistEncoder
        else:
            raise RuntimeError('Невозможно получить данные %s' % file_path)
        encoder.encode(self.get_data(), filename)

    def __init__(self, data):
        self._data = data

    def get_data(self):
        return copy.deepcopy(self._data)

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    HIST_PATH_1 = os.path.join(BASE_DIR, "..", 'data', 'csv_test.csv')
    hist = Hist.read(HIST_PATH_1)
    print(hist.get_data())

    for ext in ("bin", "txt", "json", "csv", "png"):
        path = os.path.join(BASE_DIR, "..", 'data', f'out_hist.{ext}')
        hist.write(path)
        print(f"[saved] {path}")