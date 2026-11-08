import cv2

"""
Абстрактная фабрика 
"""

class AbstractFactoryImageReader:
    def read_image(self, file_path):
        raise NotImplementedError()


class BinImageReader(AbstractFactoryImageReader):

    def read_image(self, file_path):
        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Не удалось прочитать файл: {file_path}")
        # Otsu сам подбирает порог по гистограмме
        _, binary = cv2.threshold(
            image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary


class MonochromeImageReader(AbstractFactoryImageReader):

    def read_image(self, file_path):
        image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"Не удалось прочитать файл: {file_path}")
        return image


class ColorImageReader(AbstractFactoryImageReader):

    def read_image(self, file_path):
        image = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Не удалось прочитать файл: {file_path}")
        return image


def get_image_reader(ident):

    readers = {
        0: BinImageReader,
        1: MonochromeImageReader,
        2: ColorImageReader,
    }
    try:
        return readers[ident]()
    except KeyError:
        raise ValueError(
            f"Неизвестный тип изображения: {ident!r}. "
            f"Допустимо: {list(readers)}")


if __name__ == "__main__":
    for i in range(3):
        print(get_image_reader(i))

    import os
    base = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base, "..", "data", "1.jpg")

    for ident, name in [(0, "bin"), (1, "mono"), (2, "color")]:
        reader = get_image_reader(ident)
        img = reader.read_image(img_path)
        if img is None:
            print(f"{name}: файл не найден")
            continue
        print(f"{name}: shape={img.shape}, dtype={img.dtype}")