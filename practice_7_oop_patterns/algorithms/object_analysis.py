"""
Шаблонный метод (Template method)
"""
import cv2
import os
import numpy as np

class ObjectAnalysis(object):
    def template_method(self, image):

        image = self.noise_filtering(image)
        data = self.segmentation(image)
        data = self.object_parameters(data)

        return data

    def noise_filtering(self, image):
        raise NotImplementedError()

    def segmentation(self, data):
        raise NotImplementedError()

    def object_parameters(self, data):
        (image, data) = data
        (numLabels, labels, stats, centroids) = data
        x = []
        y = []
        w = []
        h = []
        area = []
        for i in range(1, numLabels):
            # extract the connected component statistics for the current
            # label
            x.append(stats[i, cv2.CC_STAT_LEFT])
            y.append(stats[i, cv2.CC_STAT_TOP])
            w.append(stats[i, cv2.CC_STAT_WIDTH])
            h.append(stats[i, cv2.CC_STAT_HEIGHT])
            area.append(stats[i, cv2.CC_STAT_AREA])

        return (x, y, w, h, area)


class BinaryImage(ObjectAnalysis):
    def __init__(self):
        pass

    def noise_filtering(self, image):
        median = cv2.medianBlur(image, 5)
        return median

    def segmentation(self, image):
        output = cv2.connectedComponentsWithStats(
            image,
            4, # connectivity
            cv2.CV_32S)
        return (image, output)

class MonochromeImage(BinaryImage):
    def __init__(self):
        pass

    def noise_filtering(self, image):
        return cv2.GaussianBlur(image, (5, 5), 0)

    def segmentation(self, image):
        edges = cv2.Canny(image, 100, 200)

        # Параметры объектов по умолчанию:
        # connectedComponentsWithStats по бинарному изображению границ
        output = cv2.connectedComponentsWithStats(
            edges,
            4,  # connectivity
            cv2.CV_32S
        )
        return (edges, output)

class ColorImage(MonochromeImage):
    def __init__(self):
        pass

    def segmentation(self, image):
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        edges = cv2.Canny(gray, 100, 200)

        output = cv2.connectedComponentsWithStats(
            edges,
            4,
            cv2.CV_32S
        )
        return (edges, output)

"""
Декоратор - структурный паттерн
"""

class FilteredAnalysis(ObjectAnalysis):
    def __init__(self, obj):
        self._proc = obj

    def template_method(self, image):
        result = self._proc.template_method(image)
        if result is None:
            return None

        if len(result) == 5:
            (_x, _y, _w, _h, _area) = result
            hu_in = None
        else:
            (_x, _y, _w, _h, _area, hu_in) = result

        x, y, w, h, area, hu_out = [], [], [], [], [], []
        for i in range(len(_area)):
            if 10 < _area[i] < 2500:
                x.append(_x[i]); y.append(_y[i])
                w.append(_w[i]); h.append(_h[i])
                area.append(_area[i])
                if hu_in is not None:
                    hu_out.append(hu_in[i])

        if hu_in is not None:
            return (x, y, w, h, area, hu_out)
        return (x, y, w, h, area)

class HuMomentsAnalysis(ObjectAnalysis):

    def __init__(self, obj):
        self._proc = obj

    def template_method(self, image):
        filtered = self._proc.noise_filtering(image)
        seg_data = self._proc.segmentation(filtered)
        if seg_data is None:
            return None

        (seg_image, output) = seg_data
        (numLabels, labels, stats, centroids) = output

        x, y, w, h, area, hu = [], [], [], [], [], []
        for i in range(1, numLabels):
            x.append(int(stats[i, cv2.CC_STAT_LEFT]))
            y.append(int(stats[i, cv2.CC_STAT_TOP]))
            w.append(int(stats[i, cv2.CC_STAT_WIDTH]))
            h.append(int(stats[i, cv2.CC_STAT_HEIGHT]))
            area.append(int(stats[i, cv2.CC_STAT_AREA]))

            # Hu-моменты берём из маски текущего объекта
            mask = (labels == i).astype(np.uint8)
            m = cv2.moments(mask)
            hu.append(cv2.HuMoments(m).flatten())  # shape (7,)

        return (x, y, w, h, area, hu)


def log_hu(hu_vec):
    return -np.sign(hu_vec) * np.log10(np.abs(hu_vec) + 1e-30)


if __name__== '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGE_PATH_1 = os.path.join(BASE_DIR, "..", 'data', '1.jpg')
    IMAGE_PATH_2 = os.path.join(BASE_DIR, "..", 'data', '2.jpg')
    IMAGE_PATH_3 = os.path.join(BASE_DIR, "..", 'data', '3.png')


    print("Binary Image Processing")
    bin_segm = BinaryImage()
    (x,y,w,h,area) = bin_segm.template_method(cv2.imread(IMAGE_PATH_1, cv2.IMREAD_GRAYSCALE))
    for i in range(len(area)):
            print([x[i], y[i], w[i],h[i],area[i]])

    print("Monochrome Image Processing")
    mono_segm = MonochromeImage()
    (x, y, w, h, area) = mono_segm.template_method(cv2.imread(IMAGE_PATH_2, cv2.IMREAD_GRAYSCALE))
    for i in range(len(area)):
        print([x[i], y[i], w[i], h[i], area[i]])

    print("Color Image Processing")
    color_segm = ColorImage()
    (x, y, w, h, area) = color_segm.template_method(cv2.imread(IMAGE_PATH_3, cv2.IMREAD_COLOR))
    for i in range(len(area)):
        print([x[i], y[i], w[i], h[i], area[i]])

    print("Decorated Binary Image Processing")
    filt_bin = FilteredAnalysis(BinaryImage())
    (x, y, w, h, area) = filt_bin.template_method(cv2.imread(IMAGE_PATH_1, cv2.IMREAD_GRAYSCALE))
    for i in range(len(area)):
            print([x[i], y[i], w[i],h[i],area[i]])

    proc1 = HuMomentsAnalysis(BinaryImage())
    (x, y, w, h, area, hu) = proc1.template_method(cv2.imread(IMAGE_PATH_2, cv2.IMREAD_GRAYSCALE))
    for i in range(len(area)):
        print(f"obj {i}: area={area[i]}, hu[0]={hu[i][0]:.3e}")

    # Hu + фильтр по площади (FilteredAnalysis снаружи)
    proc2 = FilteredAnalysis(HuMomentsAnalysis(BinaryImage()))
    (x, y, w, h, area, hu) = proc2.template_method(cv2.imread(IMAGE_PATH_2, cv2.IMREAD_GRAYSCALE))
