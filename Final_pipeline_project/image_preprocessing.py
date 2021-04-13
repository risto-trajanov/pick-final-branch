import scipy.ndimage
from typing import Tuple, Union
import numpy as np
import cv2
import math
from deskew import determine_skew


class ImagePreprocessing:

    def __init__(self):
        pass

    @staticmethod
    def colour_transform(image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        th2 = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 9)

        return th2

    @staticmethod
    def rotation_transformation4(image):
        edged_image = cv2.Canny(image, 100, 100, apertureSize=3)
        lines = cv2.HoughLinesP(edged_image, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

        angles = []
        for x1, y1, x2, y2 in lines[0]:
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 3)

        for line in lines:
            for x1, y1, x2, y2 in line:
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                angles.append(angle)

        median_angle = float(np.median(angles))
        rotated_image = scipy.ndimage.rotate(image, median_angle, cval=255)
        return rotated_image

    @staticmethod
    def rotate(image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]) -> np.ndarray:
        if angle is not None:
            old_width, old_height = image.shape[:2]
            angle_radian = math.radians(angle)
            width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
            height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

            image_center = tuple(np.array(image.shape[1::-1]) / 2)
            rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
            rot_mat[1, 2] += (width - old_width) / 2
            rot_mat[0, 2] += (height - old_height) / 2
            return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)
        return image

    @staticmethod
    def rotation_transformation(image):
        img = cv2.resize(image, (int(image.shape[1] / 8), int(image.shape[0] / 8)), cv2.INTER_AREA)
        angle = determine_skew(img)
        rotated = ImagePreprocessing.rotate(image, angle, (255, 255, 255))
        return rotated

    @staticmethod
    def preprocess(image_path, result_path=None):
        image = cv2.imread(image_path)
        image = ImagePreprocessing.colour_transform(image)
        image = ImagePreprocessing.rotation_transformation(image)
        if result_path is not None:
            cv2.imwrite(result_path, image)
        return image
