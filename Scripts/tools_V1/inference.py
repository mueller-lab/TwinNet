import cv2
from datetime import datetime
import glob
import itertools
import json
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_io as tfio


class SNNUtilsEmbeddings:
    """
    This class is part of the toolset for usage of siamese network (SNN) on evaluation purposes.
    This artificial neural network based on EfficientNet or ResNet architecture was trained with
    the intention to perform similarity analyses between different images of embryos.

    This part of the toolset is used to manage embedding generation.
    """
    def __init__(self, size_img, size_img_min, **kwargs):
        self.ljust = 50
        self.size_img = size_img
        self.size_img_min = size_img_min
        self.utils_general = SNNUtilsGeneral()
        self.utils_images = SNNUtilsImages(self.size_img, self.size_img_min, **kwargs)
        self.utils_paths = SNNUtilsPaths()

    @staticmethod
    def fn_array_to_embedding(array_imgs, model_embedding):
        """Generate an array of embeddings from an array of images using the specified embedding model."""
        if model_embedding.name in ['Embedding_resnet50', 'Embedding_resnet101']:
            array_imgs = tf.keras.applications.resnet.preprocess_input(array_imgs)
        embedding = model_embedding(array_imgs)
        return embedding

    @staticmethod
    def fn_embeddings_combine(embeddings_a, embeddings_b):
        """Combine two embedding arrays for calculation of similarities.

        Parameters
        ----------
        embeddings_a: numpy.ndarray
        embeddings_b: numpy.ndarray
        """
        embedding_combinations = list(itertools.product(list(enumerate(embeddings_a)), list(enumerate(embeddings_b))))
        return embedding_combinations

    def dir_to_imgs_to_embeddings(self, model_embedding, path_dir):
        """
        From a directory load all image paths and images.
        Calculate embeddings for images and return embeddings as list.
        """
        paths_imgs = self.utils_paths.dir_to_img_paths(path_dir)
        array_imgs = self.utils_images.fn_images_tiff_parse(paths_imgs)
        embeds_imgs = self.imgs_to_embeddings(model_embedding, array_imgs)
        return embeds_imgs

    def imgs_to_embeddings(self, model_embedding, array_images):
        """Generate embeddings from batch."""
        list_image_segments = self.utils_images.fn_images_slice(array_images)
        embeddings = list()
        num_batches = len(list_image_segments)

        for i in range(num_batches):
            self.utils_general.fn_info_string(f'[LOADING] Image embeddings {i + 1}/{num_batches} ...'.ljust(self.ljust),
                                              ef='\r')
            batch_array = list_image_segments[i]
            embeddings.extend(self.fn_array_to_embedding(batch_array, model_embedding))
        self.utils_general.fn_info_string(f'[DONE] Image embeddings {num_batches}/{num_batches}'.ljust(self.ljust),
                                          ef='\r')
        return np.array(embeddings)


class SNNUtilsGeneral:
    """
    This class is part of the toolset for usage of siamese network (SNN) on evaluation purposes.
    This artificial neural network based on EfficientNet or ResNet architecture was trained with
    the intention to perform similarity analyses between different images of embryos.

    This part of the toolset contains commonly used functions.
    """
    @staticmethod
    def fn_info_string(string, **kwargs):
        """Convenience function to print text with standardized format."""
        info_string = f'{string}'
        if 'ef' in kwargs and kwargs['ef'] == '\n\n':
            print(info_string, end='\n')
            print('-' * len(info_string))
        else:
            print(info_string, end=kwargs.get('ef', ''))

    @staticmethod
    def fn_json_load(path_json):
        """Load json file."""
        with open(path_json, 'rb') as JsonFile:
            content = json.load(JsonFile)
        return content

    @staticmethod
    def fn_json_write(content, path_dst):
        """Write JSON serializable objects to a JSON file."""
        if path_dst.endswith('.json'):
            pass
        else:
            path_dst = f'{path_dst}/{datetime.today().strftime("%Y-%m-%d")}_inputs.json'
        with open(path_dst, 'w') as file_json:
            json.dump(content, file_json, indent=4)
        print(f'Saved file to {path_dst}.')
        file_json.close()

    @staticmethod
    def fn_validate_length_equal(inputs, fn_name):
        for i in range(len(inputs)):
            assert len(inputs[i]) == len(inputs[i + 1]),\
                f"{fn_name}: File lengths do not match." \
                f"{len(inputs[i])} vs {len(inputs[i + 1])}."


class SNNUtilsImages:
    """
    This class is part of the toolset for usage of siamese network (SNN) on evaluation purposes.
    This artificial neural network based on EfficientNet or ResNet architecture was trained with
    the intention to perform similarity analyses between different images of embryos.

    This part of the toolset is used to manage image handling.
    """
    def __init__(self, size_img, size_img_min, **kwargs):
        self.ljust = 50  # Changed on 2023-02-06 from 10 to 50
        self.model_group = kwargs.get('model_group', 'resnet')
        self.size_batch = 50
        self.size_img = size_img
        self.size_img_min = size_img_min
        self.shape_img = (size_img, size_img, 3)
        self.utils_general = SNNUtilsGeneral()

    @staticmethod
    def fn_img_center(img):
        """Calculate center of image array."""
        return int(img.shape[0] / 2), int(img.shape[1] / 2)

    def fn_image_parse_cv2(self, path_img):
        """Load image array."""
        img = cv2.imread(path_img, cv2.IMREAD_COLOR)
        centery, centerx = self.fn_img_center(img)
        img = img[int(centery - self.size_img_min / 2):int(centery + self.size_img_min / 2),
                  int(centerx - self.size_img_min / 2):int(centerx + self.size_img_min / 2)]
        img = cv2.resize(img, (self.size_img, self.size_img))
        assert img.shape == self.shape_img
        return img

    def fn_images_parse_cv2(self, paths_images):
        """Load multiple images from paths to numpy array with cv2."""
        image_segments = list()
        for path_image in paths_images:
            try:
                image_segment = self.fn_image_parse_cv2(path_image)
                image_segments.append(image_segment)
                # if self.model_group == 'resnet':
                #     image_segment /= 255
            except cv2.error:
                # print('ERROR OPENCV: ', well_file[self.key_image_path], embryo_segment)
                pass
        return np.array(image_segments)

    def fn_image_tiff_parse(self, path_img):
        """Load TIFF image from path."""
        img = tf.io.read_file(path_img)
        img = tfio.experimental.image.decode_tiff(img)
        img = tf.cast(img, tf.float32)
        img = tf.image.resize_with_crop_or_pad(img, self.size_img_min, self.size_img_min)
        img = tf.reshape(img, (self.size_img_min, self.size_img_min, 4))
        img = tf.image.resize(img, (self.size_img, self.size_img))
        img = tfio.experimental.color.rgba_to_rgb(img)
        # img = tf.keras.applications.resnet_v2.preprocess_input(img)
        return img

    def fn_images_tiff_parse(self, paths_images, **kwargs):
        """Load multiple tiff images from paths to numpy array with tfio."""
        image_segments = list()
        num_images = len(paths_images)

        for i in range(num_images):
            self.utils_general.fn_info_string(f'[LOADING] Image arrays {i + 1}/{num_images} ...'.ljust(self.ljust),
                                              ef='\r')
            path_image = paths_images[i]
            try:
                image_segment = self.fn_image_tiff_parse(path_image, **kwargs)
                # if self.model_group == 'resnet':
                #     image_segment /= 255
                image_segments.append(image_segment)
            except cv2.error:
                pass
        return np.array(image_segments)

    def fn_image_jpg_parse(self, path_img):
        """Load JPG image from path."""
        img = tf.io.read_file(path_img)
        img = tf.io.decode_jpeg(img, channels=3)
        img = tf.cast(img, tf.float32)
        img = tf.image.resize(img, (self.size_img, self.size_img))
        # img = tf.keras.applications.resnet_v2.preprocess_input(img)
        return img

    def fn_images_jpg_parse(self, paths_images, **kwargs):
        """Load multiple JPEG images from paths to numpy array with tfio."""
        image_segments = list()
        num_images = len(paths_images)

        for i in range(num_images):
            self.utils_general.fn_info_string(f'[LOADING] Image arrays {i + 1}/{num_images} ...'.ljust(self.ljust),
                                              ef='\r')

            path_image = paths_images[i]
            try:
                image_segment = self.fn_image_jpg_parse(path_image, **kwargs)
                image_segments.append(image_segment)
                # if self.model_group == 'resnet':
                #     image_segment /= 255
            except cv2.error:
                # print('ERROR OPENCV: ', well_file[self.key_image_path], embryo_segment)
                pass
        return np.array(image_segments)

    def fn_images_slice(self, array_images):
        """
        If the first dimension of an array of images is larger than self.size_batch,
        return a list of array slices with size_batch as maximum first dimension.

        Please note that this function does not need to check the array size prior to
        slicing, as this approach returns the original array if the size of the first
        dimension of this array is smaller than self.size_batch.

        Parameters
        ----------
        array_images: numpy array

        Returns
        -------
        (list_array_images:) list of numpy arrays
        """
        return [array_images[i:i+self.size_batch, :, :, :] for i in range(0, array_images.shape[0], self.size_batch)]


class SNNUtilsPaths:
    """
    This class is part of the toolset for usage of siamese network (SNN) on evaluation purposes.
    This artificial neural network based on EfficientNet or ResNet architecture was trained with
    the intention to perform similarity analyses between different images of embryos.

    This part of the toolset is used to manage input data paths.
    """
    def __init__(self):
        self.img_format = ['*CO6*.jpg', '*CO6*.tif']

    def dir_to_img_paths(self, path_src):
        """Load image paths in a specified directory."""
        paths_imgs = [p.replace('\\', '/') for f in self.img_format for p in glob.glob(f'{path_src}{f}')]
        return paths_imgs


class SNNUtilsSimilarities:
    """
    This class is part of the toolset for usage of siamese network (SNN) on evaluation purposes.
    This artificial neural network based on EfficientNet or ResNet architecture was trained with
    the intention to perform similarity analyses between different images of embryos.

    This part of the toolset is used to calculate embedding similarities. This means that
    this class takes embedding values as inputs to its functions, not images or image paths.

    It is recommended to select the structure, by which embeddings are presented to this class for
    similarity calculation, similar to the structure of image paths passed to the other SNNUtils
    classes.

    Core function of class: Comparison of two embeddings
    Higher-level functions of class: Comparison of multiple embryos.
    """
    def __init__(self):
        self.ljust = 50
        self.utils_general = SNNUtilsGeneral()

    @staticmethod
    def fn_cosine_similarity(val_a, val_b):
        """
        Calculate cosine similarity between two values 'val_a' and 'val_b'.
        """
        a = np.squeeze(val_a)
        b = np.squeeze(val_b)
        return np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))

    def cosine_similarities_multiple(self, embedding_combinations):
        """Calculate multiple cosine similarities and return as list.

        Parameters
        ----------
        embedding_combinations: list of tuples

        Returns
        -------
        cosine_similarities: list of floats
        """
        num_combs = len(embedding_combinations)
        cols = {}
        cosine_similarities = pd.DataFrame()
        for i in range(num_combs):
            # self.utils_general.fn_info_string(
            #     f'[LOADING] Image similarities {str(i + 1).zfill(6)}/{str(num_combs).zfill(6)} ...'.ljust(self.ljust),
            #     ef='\r')
            ((id_a, _val_a), (id_b, _val_b)) = embedding_combinations[i]
            if id_a in cols.keys():
                pass
            else:
                cols[id_a] = pd.Series(dtype='float64', name=id_a)
            cols[id_a].loc[id_b] = self.fn_cosine_similarity(_val_a, _val_b)

        for _k, _v in cols.items():
            cosine_similarities = pd.concat((cosine_similarities, _v.sort_index()), axis=1)
        cosine_similarities = cosine_similarities.reindex(sorted(cosine_similarities.columns), axis=1).T
        return cosine_similarities
