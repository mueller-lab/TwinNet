import cv2
from datetime import datetime
import glob
import itertools
import json
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_io as tfio
from .tngeneral import TNToolsGeneral


class TNToolsEmbeddings:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used to manage embedding generation.
    """
    def __init__(self, size_img, size_img_min, **kwargs):
        self.ljust = 50
        self.size_img = size_img
        self.size_img_min = size_img_min
        self.tools_general = TNToolsGeneral()
        self.utils_images = TNToolsImages(self.size_img,
                                          self.size_img_min,
                                          **kwargs)
        self.utils_paths = TNToolsPaths()

    @staticmethod
    def fn_array_to_embedding(array_imgs, model_embedding):
        """
        Generate an array of embeddings from an array of images
        using the specified embedding model.
        """
        embedding = model_embedding(array_imgs)
        return embedding

    @staticmethod
    def fn_embeddings_combine(embeddings_a, embeddings_b):
        """
        Combine two embedding arrays for calculation of similarities.

        Parameters
        ----------
        embeddings_a: numpy.ndarray
        embeddings_b: numpy.ndarray
        """
        embedding_combinations = list(
            itertools.product(list(enumerate(embeddings_a)),
                              list(enumerate(embeddings_b)))
        )
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
            print(f'[LOADING][Embeddings] {str(i + 1).zfill(4)}/'
                  f'{str(num_batches).zfill(4)} ...'.ljust(50),
                  end='\r')
            batch_array = list_image_segments[i]
            embeddings.extend(self.fn_array_to_embedding(batch_array,
                                                         model_embedding))
        print(f'[DONE][Embeddings] {str(num_batches).zfill(4)}/'
              f'{str(num_batches).zfill(4)}'.ljust(self.ljust))
        return np.array(embeddings)

    def list_to_embeddings(self, paths_imgs, model_embedding):
        """Generate embeddings for an image set of embryos."""
        array_imgs = self.utils_images.fn_images_tiff_parse(paths_imgs)
        embeds_imgs = self.imgs_to_embeddings(model_embedding, array_imgs)
        return embeds_imgs

    def list_to_embeddings_keep_order(self, paths_imgs, model_embedding):
        """
        Generate embeddings for an image set of embryos.
        Return embeddings as dictionary sorted by embryos.
        """
        array_imgs = self.utils_images.fn_images_tiff_parse(paths_imgs)
        embeds_imgs = self.imgs_to_embeddings(model_embedding, array_imgs)
        return {_p: _e for _p, _e in zip(paths_imgs, embeds_imgs)}


class TNToolsImages:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used to handle image data.
    """
    def __init__(self, size_img, size_img_min, size_batch=20, **kwargs):
        self.ljust = 50
        self.model_group = kwargs.get('model_group', 'resnet')
        self.size_batch = size_batch
        self.size_img = size_img
        self.size_img_min = size_img_min
        self.shape_img = (size_img, size_img, 3)
        self.tools_general = TNToolsGeneral()

    @staticmethod
    def fn_img_center(img):
        """Calculate center of image array."""
        return int(img.shape[0] / 2), int(img.shape[1] / 2)

    def fn_image_tiff_parse(self, path_img):
        """Load TIFF image from path."""
        img1 = tf.io.read_file(path_img)
        img2 = tfio.experimental.image.decode_tiff(img1)
        img3 = tf.image.resize_with_crop_or_pad(img2,
                                                self.size_img_min,
                                                self.size_img_min)
        img4 = tf.reshape(img3, (self.size_img_min, self.size_img_min, 4))
        img5 = tf.image.resize(img4, (self.size_img, self.size_img))
        img6 = tfio.experimental.color.rgba_to_rgb(img5)
        img7 = tf.keras.applications.resnet50.preprocess_input(img6)
        return img7

    def fn_images_tiff_parse(self, paths_images):
        """Load multiple tiff images from paths to numpy array with tfio."""
        image_segments = list()
        num_images = len(paths_images)

        for i in range(num_images):
            print(f'[LOADING] Image arrays '
                  f'{i + 1}/{num_images} ...'.ljust(50),
                  end='\r')
            path_image = paths_images[i]
            try:
                image_segment = self.fn_image_tiff_parse(path_image)
                image_segments.append(image_segment)
            except cv2.error:
                pass
        return np.array(image_segments)

    def fn_images_slice(self, array_images):
        """
        If the first dimension of an array of images is larger
        than self.size_batch, return a list of array slices
        with size_batch as maximum first dimension.

        Please note that this function does not need to check
        the array size prior to slicing, as this approach
        returns the original array if the size of the first
        dimension of this array is smaller than self.size_batch.

        Parameters
        ----------
        array_images: numpy array

        Returns
        -------
        list_array_images: list of numpy arrays
        """
        list_array_images = [array_images[i:i+self.size_batch, :, :, :]
                             for i in range(0, array_images.shape[0],
                                            self.size_batch)]
        return list_array_images


class TNToolsPaths:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used to manage input data paths.
    """
    def __init__(self):
        self.img_format = ['*CO6*.tif']

    def dir_to_img_paths(self, path_src):
        """
        Load image paths from a specified directory.
        """
        paths_imgs = [p.replace('\\', '/')
                      for f in self.img_format
                      for p in glob.glob(f'{path_src}{f}')]
        return paths_imgs

    def dirs_to_images_sort_indices(self, dirs_embryos):
        """
        Go through a list of embryo directories and return
        a dict of images sorted by indices.
        """
        images_embryos = dict()

        for dir_embryo in dirs_embryos:
            paths_imgs = sorted([p.replace('\\', '/')
                                for f in self.img_format
                                for p in glob.glob(f'{dir_embryo}/{f}')])
            for tp in range(len(paths_imgs)):
                if tp not in list(images_embryos.keys()):
                    images_embryos[tp] = list()
                images_embryos[tp].append(paths_imgs[tp])

        print(f'[INFO] Number of timepoints/images: '
              f'{len(images_embryos.keys())}/{len(images_embryos[1])}'.ljust(
                50))
        return images_embryos


class TNToolsSimilarities:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used to calculate embedding similarities.
    This means that this class takes embedding values as inputs
    to its methods, not images or image paths.

    It is recommended to select the structure, by which embeddings
    are presented to this class for similarity calculation, similar
    to the structure of image paths passed to the other TNTools
    classes.

    Core function of class: Comparison of two embeddings
    Higher-level functions of class: Comparison of multiple embryos.
    """
    def __init__(self):
        self.ljust = 50
        self.tools_general = TNToolsGeneral()

    @staticmethod
    def fn_calculate_similarity_differences(df_earlier, df_later):
        """
        Calculate differences between similarities and
        return as series of the same length as df_a/df_b.
        """
        assert len(df_earlier) == len(df_later), \
            'Lengths of dataframes do not match.'
        df_earlier_mean = df_earlier.mean(axis=1)
        df_later_mean = df_later.mean(axis=1)
        df_diff = df_later_mean - df_earlier_mean
        return df_earlier_mean, df_later_mean, df_diff

    @staticmethod
    def fn_cosine_similarity(val_a, val_b):
        """
        Calculate cosine similarity between two values 'val_a' and 'val_b'.
        """
        a = np.squeeze(val_a)
        b = np.squeeze(val_b)
        return np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))

    @staticmethod
    def fn_similarities_save(similarities, dir_dst, **kwargs):
        """
        Save similarities stored within dataframes in a dictionary
        to separate .csv files in a directory
        """
        signature = kwargs.get('signature', '')
        for _k, _v in similarities.items():
            print(str(_k).ljust(10), end='\r')
            path_dst = f'{dir_dst}/' \
                       f'{signature}similarities_{str(_k + 1).zfill(3)}.csv'
            _v.to_csv(path_dst)

    # def cosine_similarities_multiple(self, embedding_combinations):
    #     """Calculate multiple cosine similarities and return as list.
    #
    #     Parameters
    #     ----------
    #     embedding_combinations: list of tuples
    #
    #     Returns
    #     -------
    #     cosine_similarities: list of floats
    #     """
    #     num_combs = len(embedding_combinations)
    #     cols = {}
    #     cosine_similarities = pd.DataFrame()
    #     for i in range(num_combs):
    #         # print(f'[LOADING] Image similarities
    #         #       {str(i + 1).zfill(6)}/{str(num_combs).zfill(6)}
    #         #       ...'.ljust(self.ljust),
    #         #       end='\r')
    #         ((id_a, _val_a), (id_b, _val_b)) = embedding_combinations[i]
    #         if id_a in cols.keys():
    #             pass
    #         else:
    #             cols[id_a] = pd.Series(dtype='float64', name=id_a)
    #         cols[id_a].loc[id_b] = self.fn_cosine_similarity(_val_a, _val_b)
    #
    #     for _k, _v in cols.items():
    #         cosine_similarities = pd.concat(
    #             (cosine_similarities, _v.sort_index()), axis=1)
    #     cosine_similarities = cosine_similarities.reindex(
    #         sorted(cosine_similarities.columns), axis=1).T
    #     return cosine_similarities

    def cosine_similarities_in_batch(self, dict_embeddings_embryos):
        """
        Combine embeddings and calculate similarities
        for all combinations in embedding dictionary.
        """
        # Prepare combinations of embeddings
        combinations = list(
            itertools.combinations(list(dict_embeddings_embryos.keys()), 2))

        # Prepare lists for calculated similarities
        similarities = list()
        similarities_low_embryo_ids = list()

        # Loop through combinations of similarities
        for _k_a, _k_b in combinations:
            # Calculate similarities for each combination
            similarity = self.fn_cosine_similarity(
                dict_embeddings_embryos[_k_a],
                dict_embeddings_embryos[_k_b])
            similarities.append(similarity)
            # Append embryo ids if similarities between embryos are low
            if similarity < 0.95:
                similarities_low_embryo_ids.append([_k_a, _k_b])
        print(f'Number of combinations/similarities: '
              f'{len(combinations)}/{len(similarities)}'.ljust(50))
        return similarities, similarities_low_embryo_ids

    def cosine_similarities_reference(self,
                                      embeddings_reference_1,
                                      embeddings_reference_2,
                                      embeddings_reference_3, embeddings_test):
        """
        Loop through list of test embeddings. Calculate similarities
        between each test embedding and all reference embeddings.
        Store similarities by indices.
        """
        similarities = dict()
        for i in range(len(embeddings_test)):
            df = pd.DataFrame(columns=['Anch_sim_1',
                                       'Anch_sim_2',
                                       'Anch_sim_3'])
            for j in range(len(embeddings_reference_1)):
                if j % 100 == 0:
                    print(f'[INFO][Similarities] '
                          f'{str(i + 1).zfill(3)}/{len(embeddings_test)} '
                          f'{str(j + 1).zfill(3)}/'
                          f'{len(embeddings_reference_1)}'.
                          ljust(50),
                          end='\r')
                anch_sim_1 = self.fn_cosine_similarity(
                    embeddings_reference_1[j], embeddings_test[i])
                anch_sim_2 = self.fn_cosine_similarity(
                    embeddings_reference_2[j], embeddings_test[i])
                anch_sim_3 = self.fn_cosine_similarity(
                    embeddings_reference_3[j], embeddings_test[i])

                df.loc[j] = [anch_sim_1, anch_sim_2, anch_sim_3]
            similarities[i] = df

        return similarities
