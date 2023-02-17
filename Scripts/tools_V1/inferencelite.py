# Creation date: 2022-10-22 12:19 PM
# Author: Nikan Toulany
# This script contains functions which I commonly used in
# evaluation and plotting scripts.

import cv2
import glob
import numpy as np
import pathlib
import sys
import tensorflow as tf
import tensorflow_io as tfio
import warnings

warnings.filterwarnings(action='once')

from .inference import SNNUtilsEmbeddings as ToolsEmbeddings
from .general import SNNToolset

class ToolsInferenceLite:
    """
    Collection of commonly used tools for image
    preprocessing and embedding generation
    for inference purposes of TN.
    """
    def __init__(self):
        self.img_size = 224
        self.img_size_min = 400
        self.tools_embeddings = ToolsEmbeddings(self.img_size, self.img_size_min)
        self.tools_general = SNNToolset()

    @staticmethod
    def fn_cosine_similarity(val_a, val_b):
        """
        Calculate cosine similarity between two values 'val_a' and 'val_b'.
        """
        a = np.squeeze(val_a)
        b = np.squeeze(val_b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def fn_image_tiff_parse(self, path_img):
        """Load TIFF image from path."""
        img1 = tf.io.read_file(path_img)
        img2 = tfio.experimental.image.decode_tiff(img1)
        img3 = tf.image.resize_with_crop_or_pad(img2,
                                                self.img_size_min,
                                                self.img_size_min)
        img4 = tf.reshape(img3,
                          (self.img_size_min, self.img_size_min, 4))
        img5 = tf.image.resize(img4,
                               (self.img_size, self.img_size))
        img6 = tfio.experimental.color.rgba_to_rgb(img5)
        img7 = tf.keras.applications.resnet50.preprocess_input(img6)
        return img7

    def fn_images_tiff_parse(self, paths_images, **kwargs):
        """
        Load multiple tiff images from paths to numpy array
        with tfio.
        """
        image_segments = list()
        num_images = len(paths_images)

        for i in range(num_images):
            print(f'[LOADING] Image arrays {i + 1}/{num_images} ...'
                  .ljust(50), end='\r')
            path_image = paths_images[i]
            try:
                image_segment = self.fn_image_tiff_parse(path_image)
                image_segments.append(image_segment)
            except cv2.error:         
                pass
        return np.array(image_segments)

    def fn_similarities_load(self, dir_dst, **kwargs):
        """
        This function loads similarities from a specified directory.

        Parameters
        ----------
        dir_dst: str
            Path to directory where similarities
            should be loaded from.
        """
        #print("Here")
        pattern_glob = kwargs.get('pat_sims', f'{dir_dst}/*_similarities_tp*.json')
        paths_sims = sorted(glob.glob(pattern_glob))
        #paths_sims = glob.glob(pattern_glob)
        #for path_sim in paths_sims:
       # 	print(path_sim)
        similarities = [
            self.tools_general.fn_json_load(path_sim)           
            for path_sim in paths_sims
        ]
        return similarities

    def fn_similarities_save(self, dir_dst, similarities, **kwargs):
        """
        This function takes a list of lists and saves each
        list to a separate .json, .npy and .mat file.

        Parameters
        ----------
        dir_dst: str
            Path to directory where similarities
            should be saved to.
        similarities: list
            List of list with similarity values
            as floats.
        """
        similarities = [[float(a) for a in b] for b in similarities]
        for i in range(2, len(similarities) + 1):
            tp = f"tp{str(i).zfill(4)}"
            embryo_id = str(kwargs.get('embryo_id', 'E000'))
            p_dst_base = f"{dir_dst}/20221020_{embryo_id}_similarities_{tp}"
            p_dst_json = f"{p_dst_base}.json"
            p_dst_mat = f"{p_dst_base}.mat"
            p_dst_npy = f"{p_dst_base}.npy"
            self.tools_general.fn_json_write(similarities[i - 2], p_dst_json)
            self.tools_general.fn_mat_write({f'sims_{tp}': np.array(similarities[i - 2])},
                                            p_dst_mat)
            self.tools_general.fn_npy_write(np.array(similarities[i - 2]), p_dst_npy)

    @staticmethod
    def fn_stem_name_experiment_embryo(path_image):
        """
        Convert an image path to a standardized embryo name
        with information on experiment number, well, position
        and embryo number.

        Parameters
        ----------
        path_image: str
            Image path of format X:/.../exp_num-[...]/
            -well_pos/embryo_num/img_name.tif

        Returns
        -------
        exp_emb_id: str
            Formatted to exp_num--well_pos--embryo_num
        """
        p = pathlib.PurePath(path_image)
        exp_num = p.parent.parent.parent.stem[:]
        well_pos = p.parent.parent.stem[:]
        embryo_num = p.parent.stem
        exp_emb_id = f"{exp_num}--{well_pos}--{embryo_num}"
        return exp_emb_id

    def dir_embryo_to_similarities_self(self, path_dir, model_embedding):
        """
        Perform following steps for analysis of image sequence
        with TN:
        1. Load image paths
        2. Load image arrays
        3. Generate embeddings
        4. Calculate similarities between embeddings

        Parameters
        ----------
        path_dir: str
            Path to embryo directory containing image files
            in .TIF format
        model_embedding: keras.engine.functional.Functional
            Model to use for generation of embeddings.

        Returns
        -------
        similarities: list
            This list contains a sublist for each image, for which
            similarities were calculated with previous images.
        """
        images = [p.replace('\\', '/') for p in sorted(glob.glob(f'{path_dir}/*.tif'))]
        #print("Here")
        embeddings = self.list_to_embeddings(images, model_embedding)
        similarities = self.sequence_embeddings_to_pyramid_similarities(embeddings)
        return images, embeddings, similarities

    def list_to_embeddings(self, list_embryos_images, model_embedding):
        """Generate embeddings for an image set of embryos."""
        array_imgs = self.fn_images_tiff_parse(list_embryos_images)

        embeds_imgs = self.tools_embeddings.imgs_to_embeddings(model_embedding,
                                                               array_imgs)
        return embeds_imgs

    def sequence_embeddings_to_pyramid_similarities(self, embeddings):
        """
        Loop through list of embeddings. Calculate similarities between
        each embedding and all of its previous embeddings.
        """
        similarities = list()

        for _k in range(1, len(embeddings)):
            sims = list()

            for _j in range(len(embeddings[:_k])):
                similarity = self.fn_cosine_similarity(embeddings[_k],
                                                       embeddings[_j])
                sims.append(similarity)
            similarities.append(sims)
        return similarities

