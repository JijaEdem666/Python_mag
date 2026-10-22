"""
Шаблонный метод (Template method)
"""
import cv2
import os

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
        (_x, _y, _w, _h, _area) = self._proc.template_method(image)
        x = []
        y = []
        w = []
        h = []
        area = []

        for i in range(len(_area)):
            if _area[i] > 10 and _area[i] < 2500:
                x.append(_x[i])
                y.append(_y[i])
                w.append(_w[i])
                h.append(_h[i])
                area.append(_area[i])

        return (x,y,w,h,area)


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
