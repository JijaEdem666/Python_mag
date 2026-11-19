import numpy as np
from functools import partial

def linear_traversal(h, w):
    for r in range(h):
        for c in range(w):
            yield r, c


def zigzag_traversal(h, w):
    for r in range(h):
        if r % 2 == 0:
            cols = range(w)
        else:
            cols = range(w - 1, -1, -1)
        for c in cols:
            yield r, c


def spiral_center_traversal(h, w):
    if h <= 0 or w <= 0:
        return

    r, c = h // 2, w // 2
    visited = set()

    def add_cell(rr, cc):
        if 0 <= rr < h and 0 <= cc < w and (rr, cc) not in visited:
            visited.add((rr, cc))
            return True
        return False

    if add_cell(r, c):
        yield r, c

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    step = 1
    di = 0

    while len(visited) < h * w:
        for _ in range(2):
            dr, dc = directions[di % 4]
            for _ in range(step):
                r += dr
                c += dc
                if add_cell(r, c):
                    yield r, c
            di += 1
        step += 1

def _peano_id(r, c, s):
    return r, c


def _peano_flip_v(r, c, s):
    return s - 1 - r, c


def _peano_flip_h(r, c, s):
    return r, s - 1 - c


def _peano_rot180(r, c, s):
    return s - 1 - r, s - 1 - c

_PEANO_PATTERN = [
    (0, 0, _peano_id),
    (0, 1, _peano_flip_v),
    (0, 2, _peano_id),
    (1, 2, _peano_flip_h),
    (1, 1, _peano_rot180),
    (1, 0, _peano_flip_h),
    (2, 0, _peano_id),
    (2, 1, _peano_flip_v),
    (2, 2, _peano_id),
]

def peano_curve(n):
    if n == 0:
        return [(0, 0)]

    prev = peano_curve(n - 1)
    sub = 3 ** (n - 1)
    result = []

    for br, bc, transform in _PEANO_PATTERN:
        for r, c in prev:
            tr, tc = transform(r, c, sub)
            result.append((br * sub + tr, bc * sub + tc))

    return result


def peano_traversal(h, w):
    n = 0
    while 3 ** n < max(h, w):
        n += 1

    for r, c in peano_curve(n):
        if r < h and c < w:
            yield r, c


to_gray = lambda rgb: (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
).astype(np.float64)

def convolution_stream(image, kernel, traversal):

    image = np.asarray(image, dtype=np.float64)
    kernel = np.asarray(kernel, dtype=np.float64)

    h, w = image.shape
    kh, kw = kernel.shape
    dr, dw = kh // 2, kw // 2

    def process(rc):
        r, c = rc
        patch = image[r - dr:r + dr + 1, c - dw:c + dw + 1]
        value = float(np.sum(patch * kernel))
        return r, c, value

    valid_indices = (
        (r, c)
        for r, c in traversal(h, w)
        if dr <= r < h - dr and dw <= c < w - dw
    )

    return map(process, valid_indices)


def apply_convolution(image, traversal, kernel):

    image = np.asarray(image, dtype=np.float64)
    out = image.copy()

    for r, c, value in convolution_stream(image, kernel, traversal):
        out[r, c] = value

    return out

def mse(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    return float(np.mean((a - b) ** 2))


mean_kernel = np.ones((3, 3), dtype=np.float64) / 9.0
gauss_kernel = np.array([
    [1, 2, 1],
    [2, 4, 2],
    [1, 2, 1]
], dtype=np.float64) / 16.0

mean_filter = partial(apply_convolution, kernel=mean_kernel)
gauss_filter = partial(apply_convolution, kernel=gauss_kernel)





img = np.random.rand(15, 17)

traversals = {
    "linear": linear_traversal,
    "spiral": spiral_center_traversal,
    "zigzag": zigzag_traversal,
    "peano": peano_traversal,
}


for name, traversal in traversals.items():
    points = list(traversal(*img.shape))
    print(f"{name}: точек = {len(points)}, уникальных = {len(set(points))}")


ref_mean = mean_filter(img, linear_traversal)
ref_gauss = gauss_filter(img, linear_traversal)

print("\nMSE для фильтра среднего:")
for name, traversal in traversals.items():
    result = mean_filter(img, traversal)
    print(f"  {name}: {mse(ref_mean, result):.12f}")

print("\nMSE для фильтра Гаусса:")
for name, traversal in traversals.items():
    result = gauss_filter(img, traversal)
    print(f"  {name}: {mse(ref_gauss, result):.12f}")


rgb = np.random.rand(10, 12, 3)
gray = to_gray(rgb)
print("\nGrayscale shape:", gray.shape)