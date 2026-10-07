import numpy as np
import cv2

def gamma_correction(image, gamma):
    if gamma <= 0:
        raise ValueError('Gamma must be > 0')
    inv_gamma = 1.0 / gamma
    table = np.array(
        [((i / 255.0) ** inv_gamma) * 255 for i in range(256)]
    ).astype(np.uint8)
    return cv2.LUT(image, table)