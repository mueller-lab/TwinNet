import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf
import tensorflow_io as tfio
from collections import OrderedDict
from . import image_tasks

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
    except RuntimeError as e:
        print(e)


class PredictionTasks:
    """Methods depending on tensorflow or related to model prediction."""
    
    def __init__(self):
        self.format_ljust = 50
        self.IT_INSTANCE = image_tasks.ImageTasks()

    @staticmethod
    def img_tif_load_to_tensor(path):
        """Load an RGBA TIFF image to a tensor."""
        image = tf.io.read_file(path)
        image = tfio.experimental.image.decode_tiff(image)
        image = tfio.experimental.color.rgba_to_rgb(image)
        image = tf.expand_dims(image, 0)

        return image

    @staticmethod
    def array_to_tensor(img_array):
        """Convert an image from numpy.ndarray to a tf.Tensor."""
        img_tensor = tf.convert_to_tensor(img_array)
        img_tensor = img_tensor[tf.newaxis, ...]

        return img_tensor
    
    def img_load_to_tensor(self, path):
        """Load an RGB JPEG or PNG image to a tf.Tensor."""
        img_array = self.IT_INSTANCE.img_load_to_array(path)
        img_tensor = self.array_to_tensor(img_array)
        
        return img_tensor

    def load_model(self, path_model_segmentation):
        """Load the image segmentation model."""
        print("[LOADING][SEGMENTATION MODEL] ...".ljust(self.format_ljust),
              end='\r')
        model = tf.saved_model.load(str(path_model_segmentation))
        print("[INFO][SEGMENTATION MODEL] Loaded.".ljust(self.format_ljust),
              end='\n')
        return model

    def inference(self, model_segmentation, path):
        """Run inference on a single image in EagerTensor format."""
        try:
            img_tensor = self.img_load_to_tensor(path)
        except Exception as e:
            print('DEBUG --prediction_tasks/inference (Error 1) -- \n', e)

        try:
            model_segmentation_signature = \
                model_segmentation.signatures['serving_default']
            output = model_segmentation_signature(img_tensor)
        except Exception as e:
            print('DEBUG --prediction_tasks/inference (Error 2) -- \n', e)

        try:
            num_detections = int(output.pop('num_detections'))
            output = {key: value[0, :num_detections].numpy()
                      for key, value in output.items()}
            output['num_detections'] = num_detections

            output['detection_classes'] = \
                output['detection_classes'].astype(np.int64)
        except Exception as e:
            print('DEBUG --prediction_tasks/inference (Error 3) -- \n', e)

        return output, img_tensor

    @staticmethod
    def boxes_threshold(output, threshold, shape):
        """
        Sort out predictions below a prediction confidence threshold.
        
        This function is used to clear low-probability/confidence
        predictions from the prediction dictionary. From the original
        segmentation model output it creates a new dictionary containing
        only predictions above a defined threshold value.
        
        Parameters
        ----------
        output: dictionary
            Segmentation model prediction stored as dictionary.
        threshold: float
            The minimal probability value of prediction
            to list a prediction
        shape: int
            Image shape (necessary to adjust original box predictions
            that range from 0 to 1)
        
        Returns
        -------
        bboxes: ordered dictionary
            Filtered and re-adjusted model predictions with
            class, score, and box location for each prediction

        Raises
        ------
        None.          
        """
        bboxes = OrderedDict()
        for i in range(len(output['detection_scores'])):
            if output['detection_scores'][i] > threshold:
                bboxes[i] = [output['detection_classes'][i],
                             output['detection_scores'][i],
                             [a * shape
                              for a
                              in output['detection_boxes'][i]]]
            else:
                break
        
        return bboxes
