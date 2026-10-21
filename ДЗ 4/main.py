import math
from typing import List, Tuple, Optional


class Image:
    def __init__(self, width, height, data):
        self.width = width
        self.height = height
        self.data = data

    def copy(self):
        raise NotImplementedError


class BinaryImage(Image):
    def __init__(self, width, height, data=None):
        if data is None:
            data = [[0] * width for _ in range(height)]
        super().__init__(width, height, data)

    def copy(self):
        return BinaryImage(
            self.width, self.height,
            [row[:] for row in self.data]
        )


class MonochromeImage(Image):
    def __init__(self, width, height, data=None):
        if data is None:
            data = [[0] * width for _ in range(height)]
        super().__init__(width, height, data)

    def copy(self):
        return MonochromeImage(
            self.width, self.height,
            [row[:] for row in self.data]
        )


class ColorImage(Image):
    def __init__(self, width, height, data=None):
        if data is None:
            data = [[(0, 0, 0)] * width for _ in range(height)]
        super().__init__(width, height, data)

    def copy(self):
        return ColorImage(
            self.width, self.height,
            [row[:] for row in self.data]
        )


class ImageConverter:
    @staticmethod
    def _clamp(v, lo = 0, hi = 255):
        return max(lo, min(hi, int(round(v))))

    @staticmethod
    def monochrome_to_monochrome(img: MonochromeImage, target_mean = 128.0, target_std = 64.0):
        vals = [v for row in img.data for v in row]
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals)
        std = math.sqrt(var)

        if std < 1e-9:
            return img.copy()

        out = [
            [ImageConverter._clamp((v - mean) / std * target_std + target_mean)
             for v in row]
            for row in img.data
        ]
        return MonochromeImage(img.width, img.height, out)

    @staticmethod
    def color_to_color(img: ColorImage, target_mean = (128, 128, 128), target_std = (64, 64, 64)):
        channels = [
            [[p[c] for p in row] for row in img.data]
            for c in range(3)
        ]

        out_channels = []
        for c in range(3):
            vals = [v for row in channels[c] for v in row]
            mean = sum(vals) / len(vals)
            var = sum((v - mean) ** 2 for v in vals) / len(vals)
            std = math.sqrt(var)

            if std < 1e-9:
                out_channels.append([row[:] for row in channels[c]])
            else:
                out_channels.append([
                    [ImageConverter._clamp((v - mean) / std * target_std[c] + target_mean[c])
                     for v in row]
                    for row in channels[c]
                ])

        out = [
            [
                (out_channels[0][y][x],
                 out_channels[1][y][x],
                 out_channels[2][y][x])
                for x in range(img.width)
            ]
            for y in range(img.height)
        ]
        return ColorImage(img.width, img.height, out)

    @staticmethod
    def binary_to_binary(img: BinaryImage):
        return img.copy()

    @staticmethod
    def color_to_monochrome(img: ColorImage):
        out = [
            [(r + g + b) // 3 for (r, g, b) in row]
            for row in img.data
        ]
        return MonochromeImage(img.width, img.height, out)

    @staticmethod
    def monochrome_to_color(img: MonochromeImage, palette):
        if len(palette) != 256:
            raise ValueError("Палитра должна содержать ровно 256 цветов")

        out = [
            [palette[v] for v in row]
            for row in img.data
        ]
        return ColorImage(img.width, img.height, out)

    @staticmethod
    def _otsu_threshold(img: MonochromeImage):
        hist = [0] * 256
        for row in img.data:
            for v in row:
                hist[v] += 1

        total = img.width * img.height
        sum_all = sum(i * hist[i] for i in range(256))

        sum_b = 0
        w_b = 0
        max_var = -1.0
        threshold = 127

        for t in range(256):
            w_b += hist[t]
            if w_b == 0:
                continue

            sum_b += t * hist[t]
            w_f = total - w_b
            if w_f == 0:
                break

            m_b = sum_b / w_b
            m_f = (sum_all - sum_b) / w_f
            var_between = w_b * w_f * (m_b - m_f) ** 2

            if var_between > max_var:
                max_var = var_between
                threshold = t

        return threshold

    @staticmethod
    def monochrome_to_binary(img: MonochromeImage, threshold = 127):
        out = [
            [1 if v > threshold else 0 for v in row]
            for row in img.data
        ]
        return BinaryImage(img.width, img.height, out)

    @staticmethod
    def binary_to_monochrome(img: BinaryImage):
        whites = [
            (x, y)
            for y in range(img.height)
            for x in range(img.width)
            if img.data[y][x] == 1
        ]

        if not whites:
            return MonochromeImage(
                img.width, img.height,
                [[0] * img.width for _ in range(img.height)]
            )

        dist = [[0.0] * img.width for _ in range(img.height)]
        max_d = 0.0

        for y in range(img.height):
            for x in range(img.width):
                if img.data[y][x] == 1:
                    d = 0.0
                else:
                    d = min(
                        math.hypot(x - wx, y - wy)
                        for wx, wy in whites
                    )
                dist[y][x] = d
                if d > max_d:
                    max_d = d

        if max_d < 1e-9:
            return MonochromeImage(
                img.width, img.height,
                [[0] * img.width for _ in range(img.height)]
            )

        out = [
            [ImageConverter._clamp(d / max_d * 255) for d in row]
            for row in dist
        ]
        return MonochromeImage(img.width, img.height, out)

    @classmethod
    def color_to_binary(cls, img: ColorImage,
                        threshold = None):
        mono = cls.color_to_monochrome(img)
        return cls.monochrome_to_binary(mono, threshold)

    @classmethod
    def binary_to_color(cls, img: BinaryImage,
                        palette):
        mono = cls.binary_to_monochrome(img)
        return cls.monochrome_to_color(mono, palette)



def print_image(img, title=""):
    if title:
        print(f"{title} ({img.width}x{img.height}):")
    for row in img.data:
        print("  ", row)

print("Бинарное -> Бинарное (без изменений)")
binary1 = BinaryImage(4, 4, [
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 0],
])
print_image(binary1, "Исходное бинарное")
binary_same = ImageConverter.binary_to_binary(binary1)
print_image(binary_same, "Результат")

print("Цветное -> Монохром ((R+G+B)/3)")
color1 = ColorImage(3, 2, [
    [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
    [(255, 255, 255), (128, 128, 128), (0, 0, 0)],
])
print_image(color1, "Исходное цветное")
mono_from_color = ImageConverter.color_to_monochrome(color1)
print_image(mono_from_color, "Монохром")


print("Монохром -> Бинарное (порог = 100)")
mono1 = MonochromeImage(4, 3, [
    [0, 50, 100, 150],
    [60, 110, 160, 210],
    [30, 80, 130, 180],
])
print_image(mono1, "Исходное монохром")
binary_manual = ImageConverter.monochrome_to_binary(mono1, threshold=100)
print_image(binary_manual, "Бинарное (порог 100)")

print("Монохром -> Бинарное (алгоритм Оцу)")
mono2 = MonochromeImage(4, 2, [
    [10, 20, 30, 40],
    [200, 210, 220, 230],
])
print_image(mono2, "Исходное монохром")
binary_otsu = ImageConverter.monochrome_to_binary(mono2)
print_image(binary_otsu, "Бинарное (Оцу)")


print("Бинарное -> Монохром (distance transform)")
binary2 = BinaryImage(5, 5, [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
])
print_image(binary2, "Исходное бинарное")
mono_dist = ImageConverter.binary_to_monochrome(binary2)
print_image(mono_dist, "Карта расстояний (0..255)")


print("Монохром -> Цветное (палитра)")

palette = [(0, 0, 0)] * 256
for i in range(256):
    if i < 85:
        palette[i] = (0, 0, i * 3)
    elif i < 170:
        palette[i] = (0, (i - 85) * 3, 0)
    else:
        palette[i] = ((i - 170) * 3, 0, 0)

mono3 = MonochromeImage(3, 1, [[50, 128, 200]])
print_image(mono3, "Исходное монохром")
color_from_mono = ImageConverter.monochrome_to_color(mono3, palette)
print_image(color_from_mono, "Цветное по палитре")


print("Монохром -> Монохром (статистическая коррекция)")
mono4 = MonochromeImage(3, 2, [
    [100, 105, 110],
    [115, 120, 125],
])
print_image(mono4, "Исходное (низкий контраст)")
corrected = ImageConverter.monochrome_to_monochrome(
    mono4, target_mean=128, target_std=64
)
print_image(corrected, "После коррекции (mean=128, std=64)")


print("Цветное -> Цветное (поканальная статистическая коррекция)")
color2 = ColorImage(2, 2, [
    [(100, 110, 120), (105, 115, 125)],
    [(110, 120, 130), (115, 125, 135)],
])
print_image(color2, "Исходное цветное")
corrected_color = ImageConverter.color_to_color(
    color2,
    target_mean=(128, 128, 128),
    target_std=(64, 64, 64)
)
print_image(corrected_color, "После поканальной коррекции")


print("Цветное -> Бинарное (цветное -> монохром -> бинарное)")
color3 = ColorImage(3, 2, [
    [(255, 0, 0), (0, 255, 0), (0, 0, 255)],
    [(255, 255, 255), (128, 128, 128), (0, 0, 0)],
])
print_image(color3, "Исходное цветное")
binary_from_color = ImageConverter.color_to_binary(color3, threshold=100)
print_image(binary_from_color, "Результат (бинарное)")


print("Бинарное -> Цветное (бинарное -> монохром -> цветное)")
binary3 = BinaryImage(4, 3, [
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 1, 0],
])
print_image(binary3, "Исходное бинарное")
palette2 = [(i, i, i) for i in range(256)]
color_from_binary = ImageConverter.binary_to_color(binary3, palette2)
print_image(color_from_binary, "Результат (цветное)")
