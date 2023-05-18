import cv2
import numpy as np
from . import directory_tasks


class ImageTasks:
    """Set of tools operating on image arrays."""
    
    def __init__(self):
        self.title = 'ImageTasks'
        self.DT_INSTANCE = directory_tasks.DirectoryTasks()

    @staticmethod
    def img_load_to_array(path):
        """Load an RGB JPEG or PNG image to a numpy.ndarray."""
        img_array = cv2.imread(path)
        return img_array

    @staticmethod
    def bbox_histogram(image, bbox):
        image = np.squeeze(image)
        ymin, xmin, ymax, xmax = bbox
        hist_original, bins_original = np.histogram(
            image[int(ymin):int(ymax), int(xmin):int(xmax)].ravel(),
            256,
            [0, 256]
        )
        hist_original = hist_original.tolist()
        bins_original = bins_original.tolist()
        image_min = int(image.min())
        image_max = int(image.max())

        return hist_original, bins_original, image_min, image_max
