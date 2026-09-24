# main.py
import ht2_module
import time
import random


def generate_2d_image(h, w):
    return [[random.uniform(0, 255) for _ in range(w)] for _ in range(h)]


def generate_3d_image(h, w, c):
    return [[[random.uniform(0, 255) for _ in range(c)] for _ in range(w)] for _ in range(h)]


def generate_kernel(kh, kw):
    return [[random.uniform(-1, 1) for _ in range(kw)] for _ in range(kh)]


def measure_time(func, *args):
    start_time = time.perf_counter()
    func(*args)
    end_time = time.perf_counter()
    return end_time - start_time


def benchmark_convert_color_vectors(count):
    vectors = [[random.uniform(0, 255), random.uniform(0, 255), random.uniform(0, 255), random.randint(0, 1)] for _ in
               range(count)]

    start_time = time.perf_counter()
    for v in vectors:
        ht2_module.convert_color_vector(v)
    end_time = time.perf_counter()
    return end_time - start_time


results = []
results.append(f"{'Функция':<25} | {'Размер входа':<25} | {'Время (сек)':<15}")

for size in [100, 200, 300]:
    for k_size in [3, 5]:
        img = generate_2d_image(size, size)
        kernel = generate_kernel(k_size, k_size)
        t = measure_time(ht2_module.convolve2d, img, kernel)
        results.append(f"{'convolve2d':<25} | {f'{size}x{size}, ядро {k_size}x{k_size}':<25} | {t:.6f}")


multichannel_filter = ht2_module.multichannel_filter_decorator(ht2_module.convolve2d)

for size in [50, 100, 150]:
    img_3d = generate_3d_image(size, size, 3)
    kernel = generate_kernel(3, 3)
    t = measure_time(multichannel_filter, img_3d, kernel)
    results.append(f"{'multichannel_filter':<25} | {f'{size}x{size}x3, ядро 3x3':<25} | {t:.6f}")

for count in [10000, 50000, 100000]:
    t = benchmark_convert_color_vectors(count)
    results.append(f"{'convert_color_vector':<25} | {f'{count} векторов':<25} | {t:.6f}")

report_filename = "timing_results.txt"
with open(report_filename, "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print(f"\nРезультаты сохранены в файл: {report_filename}")