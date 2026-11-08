
import csv
import json
import os
from collections import defaultdict

import numpy as np


class HistEncoder:
    ext = None

    @staticmethod
    def encode(data, file_path):
        raise NotImplementedError()

    @staticmethod
    def decode(file_path):
        raise NotImplementedError()


class CSVHistEncoder(HistEncoder):
    ext = ".csv"

    @staticmethod
    def encode(data, file_path):
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["feature", "bin_left", "bin_right", "count"])
            for name, (counts, edges) in data.items():
                for i in range(len(counts)):
                    w.writerow([name,
                                float(edges[i]),
                                float(edges[i + 1]),
                                int(counts[i])])

    @staticmethod
    def decode(file_path):
        rows = defaultdict(list)
        with open(file_path, "r", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f, delimiter=";"):
                rows[row["feature"]].append(
                    (float(row["bin_left"]),
                     float(row["bin_right"]),
                     int(row["count"])))
        out = {}
        for name, bins in rows.items():
            edges = np.array([b[0] for b in bins] + [bins[-1][1]],
                             dtype=np.float64)
            counts = np.array([b[2] for b in bins], dtype=np.int64)
            out[name] = (counts, edges)
        return out


class JSONHistEncoder(HistEncoder):
    ext = ".json"

    @staticmethod
    def encode(data, file_path):
        payload = {name: {"counts": counts.tolist(),
                          "edges": edges.tolist()}
                   for name, (counts, edges) in data.items()}
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    @staticmethod
    def decode(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return {name: (np.array(v["counts"], dtype=np.int64),
                       np.array(v["edges"], dtype=np.float64))
                for name, v in payload.items()}


class NPYHistEncoder(HistEncoder):
    ext = ".npz"

    @staticmethod
    def encode(data, file_path):
        arrs = {}
        for name, (counts, edges) in data.items():
            arrs[f"{name}__counts"] = counts
            arrs[f"{name}__edges"] = edges
        np.savez(file_path, **arrs)

    @staticmethod
    def decode(file_path):
        out = {}
        with np.load(file_path) as z:
            names = {k[:-len("__counts")] for k in z.files
                     if k.endswith("__counts")}
            for n in names:
                out[n] = (z[f"{n}__counts"], z[f"{n}__edges"])
        return out


class HistStorage:
    _REGISTRY = {
        "csv":  CSVHistEncoder,
        "json": JSONHistEncoder,
        "npz":  NPYHistEncoder,
    }

    def __init__(self, strategy=None):
        self._strategy = strategy

    def set_strategy(self, strategy):
        self._strategy = strategy

    @classmethod
    def by_extension(cls, file_path):
        ext = os.path.splitext(file_path)[1].lstrip(".").lower()
        if ext not in cls._REGISTRY:
            raise ValueError(f"Неизвестный формат {ext!r}. "
                             f"Доступны: {list(cls._REGISTRY)}")
        return cls(cls._REGISTRY[ext])

    def _resolve(self, file_path):
        return self._strategy or type(self).by_extension(file_path)._strategy

    def save(self, data, file_path):
        self._resolve(file_path).encode(data, file_path)

    def load(self, file_path):
        return self._resolve(file_path).decode(file_path)
