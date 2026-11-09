
import csv
import json
import sys
import struct
from collections import defaultdict

import cv2
import numpy as np


class HistEncoder:
    @staticmethod
    def encode(data, file_path):
        raise NotImplementedError()


class BinHistEncoder(HistEncoder):

    @staticmethod
    def encode(data, file_path):
        # ключи 0..255; недостающие бины -> 0.0, чтобы файл всегда был
        # ровно 1024 байта и struct.unpack у декодера не падал
        values = [float(data.get(i, 0.0)) for i in range(256)]
        with open(file_path, "wb") as f:
            f.write(struct.pack("f" * 256, *values))


class CsvHistEncoder(HistEncoder):

    @staticmethod
    def encode(data, file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for k, v in data.items():
                w.writerow([int(k), float(v)])


class TxtHistEncoder(HistEncoder):

    @staticmethod
    def encode(data, file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            for k in sorted(data):
                f.write(f"{int(k)} {float(data[k])}\n")


class JsonHistEncoder(HistEncoder):

    @staticmethod
    def encode(data, file_path):
        items = sorted(data.items())
        payload = {
            "keys":   [int(k) for k, _ in items],
            "values": [float(v) for _, v in items],
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)


class ImageHistEncoder(HistEncoder):

    WIDTH_PER_BIN = 3
    HEIGHT = 256

    @staticmethod
    def encode(data, file_path):
        H = ImageHistEncoder.HEIGHT
        W = ImageHistEncoder.WIDTH_PER_BIN * 256
        canvas = np.zeros((H, W, 3), dtype=np.uint8)

        max_v = max((float(v) for v in data.values()), default=0.0)
        if max_v <= 0:
            max_v = 1.0

        for i in range(256):
            v = float(data.get(i, 0.0))
            h = int(round(v / max_v * (H - 1)))
            x0 = i * ImageHistEncoder.WIDTH_PER_BIN
            x1 = x0 + ImageHistEncoder.WIDTH_PER_BIN - 1
            cv2.rectangle(canvas, (x0, H - 1 - h), (x1, H - 1),
                          (255, 255, 255), -1)

        if not cv2.imwrite(file_path, canvas):
            raise IOError(f"Не удалось сохранить изображение: {file_path}")