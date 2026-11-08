import os

import numpy as np

from encoder import HistStorage, CSVHistEncoder

def compute_hu_histograms(hu_list, bins=10):
    if not hu_list:
        return {}
    arr = np.asarray(hu_list, dtype=np.float64)
    out = {}
    for k in range(arr.shape[1]):
        counts, edges = np.histogram(arr[:, k], bins=bins)
        out[f"hu{k + 1}"] = (counts, edges)
    return out


def compute_area_histogram(areas, bins=10):
    counts, edges = np.histogram(np.asarray(areas, dtype=np.float64),
                                 bins=bins)
    return {"area": (counts, edges)}


def build_histograms(area, hu, bins=10):
    hist = {}
    hist.update(compute_area_histogram(area, bins=bins))
    hist.update(compute_hu_histograms(hu, bins=bins))
    return hist



def save_histograms(hist, out_dir, base_name,
                    formats=("json", "csv", "npz")):
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for fmt in formats:
        path = os.path.join(out_dir, f"{base_name}_hist.{fmt}")
        HistStorage.by_extension(path).save(hist, path)
        paths[fmt] = path
        print(f"[saved] {path}")
    return paths


def load_histograms(path):
    return HistStorage.by_extension(path).load(path)



if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "results")

    rng = np.random.default_rng(0)
    hu_list = [rng.normal(0, 1e-3, size=7) for _ in range(50)]
    areas = rng.integers(20, 2500, size=50).tolist()

    hist = build_histograms(areas, hu_list, bins=10)
    paths = save_histograms(hist, out_dir, "demo")

    for fmt, path in paths.items():
        loaded = load_histograms(path)
        keys_ok = set(loaded) == set(hist)
        data_ok = all(
            np.array_equal(loaded[k][0], hist[k][0])
            and np.allclose(loaded[k][1], hist[k][1])
            for k in hist
        )
        print(f"[{fmt}] keys_ok={keys_ok}, data_ok={data_ok}")

    storage = HistStorage()
    storage.set_strategy(CSVHistEncoder)
    storage.save(hist, os.path.join(out_dir, "explicit.bin"))
    print("[runtime] saved with CSV encoder to .bin extension")
