import glob
import numpy as np
import os
import pathlib
import re
import statistics
import tensorflow as tf

from .tngeneral import TNToolsGeneral
from .tninference import TNToolsEmbeddings
from .tninference import TNToolsImages
from .tninference import TNToolsSimilarities
from .tninference import TNToolsPaths


class TNToolsBatchComparison:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used to calculate similarities
    between objects of different groups, e.g. embryos with different
    treatment conditions.
    This class coordinates the use of two classes:
     - TNToolsBatchComparisonEmbeddings
     - TNToolsBatchComparisonSimilarities
    These subclasses contain methods for calculation of embeddings
    and similarities, respectively.
    """
    def __init__(self):
        self.tools_batch_comparison_embeddings = \
            TNToolsBatchComparisonEmbeddings()
        self.tools_batch_comparison_similarities = \
            TNToolsBatchComparisonSimilarities()
        self.tools_general = TNToolsGeneral()

    def dirs_objects_to_embeddings(self, path_dir_objects, model_embedding):
        """
        Load object images and calculate embeddings
        for image sequences of multiple objects in
        one object batch.

        Parameters
        ----------
        path_dir_objects: str
            Path to directory containing object subdirectories
            with images of the objects.
        model_embedding: keras.engine.functional.Functional
            Tensorflow model for embedding calculation.
        """
        embeddings = self.tools_batch_comparison_embeddings(
            path_dir_objects,
            model_embedding
        )
        return embeddings

    def embeddings_to_similarities(self,
                                   batch_embeddings1,
                                   batch_embeddings2):
        """
        For each object embedding in one of two groups of object
        embeddings sorted by image indices, calculate similarities
        with all object embeddings of the other group at the same
        image index.
        """
        similarities_1_to_2, similarities_2_to_1 = \
            self.tools_batch_comparison_similarities(
                batch_embeddings1,
                batch_embeddings2
            )
        return similarities_1_to_2, similarities_2_to_1

    @staticmethod
    def fn_batch_embeddings_npy_load(dir_embeddings):
        """
        Method to load embeddings from .npy files.
        'Reverse' method for 'fn_batch_embeddings_npy_save'.

        Parameters
        ----------
        dir_embeddings: str
            Path to directory in which subdirectories for acquisition
            timepoints and .npy files containing object embeddings
            are saved.

        Returns
        -------
        dict_embeddings: dict
            Dictionary, in which keys correspond to acquisition/
            analysis timepoints, values correspond to sub-
            dictionaries. The latter ones have as keys object
            IDs corresponding to the objects in the dataset in
            format 'E0XY'. The corresponding values are embeddings
            in numpy.ndarray format.
        """
        dict_embeddings = dict()
        dirs_tps = list(sorted(glob.glob(f"{dir_embeddings}/*/")))

        for dir_tp in dirs_tps:
            embs = list(sorted(glob.glob(f"{dir_tp}/*.npy")))
            dict_tp = dict()

            for emb in embs:
                dict_tp[pathlib.PurePath(emb).stem] = np.load(emb)
            dict_embeddings[int(pathlib.PurePath(dir_tp).stem)] = dict_tp
        return dict_embeddings

    def fn_batch_embeddings_npy_save(self, dict_embeddings, dir_dst):
        """
        Method to save embeddings to multiple .npy files.
        Creates a directory structure within 'dir_dst'
        similar to structure of dict_embeddings.

        Parameters
        ----------
        dict_embeddings: dict
            Dictionary, in which keys correspond to image indices,
            values correspond to sub-dictionaries. The latter ones
            have as keys object IDs corresponding to the objects in
            the dataset in format 'E0XY'. The corresponding values
            are embeddings in numpy.ndarray format.
        dir_dst: str
            Path to directory in which subdirectories for acquisition
            timepoints and .npy files containing object embeddings
            should be localized.
        """
        # Loop through dictionary
        for _k_tp, _v_tp in dict_embeddings.items():
            print(f"{str(_k_tp).zfill(5)}/"
                  f"{str(len(dict_embeddings)).zfill(5)}".ljust(20),
                  end='\r')
            dir_dst_tp = self.tools_general.fn_subdir_make(
                dir_dst,
                f"{str(_k_tp).zfill(5)}"
            )

            for _k_emb, _v_emb in _v_tp.items():
                path_dst_emb = os.path.join(dir_dst_tp, f"{_k_emb}.npy")
                np.save(path_dst_emb, _v_emb)


class TNToolsBatchComparisonEmbeddings:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This class can be used indirectly by using the class
    'TNToolsBatchComparison' to calculate embeddings
    for ordered image sequences of multiple objects in object batches,
    e.g. embryos with different treatment conditions.
    """
    def __init__(self, size_img=224, size_img_min=300):
        self.format_ljust = 50

        self.indices_images = list()

        self.mode_num_indices = 0
        self.max_num_indices = 0
        self.num_indices = list()

        self.pattern_index = '--LO(.*)--CO'

        self.size_img = size_img
        self.size_img_min = size_img_min

        self.tools_general = TNToolsGeneral()
        self.tools_embeddings = TNToolsEmbeddings(size_img=size_img,
                                                  size_img_min=size_img_min)
        self.tools_images = TNToolsImages(size_img=size_img,
                                          size_img_min=size_img_min)
        self.tools_paths = TNToolsPaths()

    def __call__(self, path_dir_objects, model_embedding):
        """
        For a set of objects in one batch of objects,
        calculate embeddings for all images of each object.

        Parameters
        ----------
        path_dir_objects: str
            Path to directory containing object subdirectories
            with images of the objects.
        model_embedding: keras.engine.functional.Functional
            Tensorflow model for embedding calculation.
        """
        # Reset variables if class was called previously
        self.__init__()
        # Load object subdirectories
        dirs_objects = self.fn_dirs_objects_glob(path_dir_objects)
        # Load images from image file paths and calculate embeddings
        embeddings_sort_by_objects = self.paths_to_embeddings(
            dirs_objects,
            model_embedding
        )
        # Sort files by indices
        embeddings_sort_by_indices = self.embeddings_sort_by_indices(
            embeddings_sort_by_objects
        )

        return embeddings_sort_by_indices

    def embeddings_sort_by_indices(self, embeddings_sort_by_objects):
        """
        Sort image segment embeddings by image indices and objects.
        """
        # Calculate the mode of the number of images per object
        self.mode_num_indices = statistics.mode(self.num_indices)
        self.max_num_indices = np.max(self.num_indices)

        # Select objects based on image numbers
        embeddings_sort_by_indices_min = {
            _k: _v
            for _k, _v
            in embeddings_sort_by_objects.items()
            if len(_v) >= self.mode_num_indices
        }

        # Prepare a dictionary to sort object images
        # by index and objects
        embeddings_sort_by_indices = {
            i: {} for i in sorted(set(self.indices_images))
        }
        # Loop through objects
        for k_obj, v_obj_embeddings in embeddings_sort_by_indices_min.items():
            # Loop through image embeddings in list of image file paths
            # of selected object
            for k_index, v_index in v_obj_embeddings.items():
                # Assign image embedding by image index and object
                # to dictionary
                embeddings_sort_by_indices[k_index][k_obj] = v_index

        return embeddings_sort_by_indices

    @staticmethod
    def fn_dirs_objects_glob(path_dir_objects):
        """
        Convenience method to glob for subdirectories within the
        root directory containing images of objects.
        """
        dirs_objects = [p.replace("\\", "/")
                        for p
                        in list(sorted(glob.glob(f"{path_dir_objects}/E*/")))]
        return dirs_objects

    def fn_index_extract(self, path_file):
        """
        Extract an index based on an index pattern from a file path.
        """
        index_img = int(
            re.search(
                self.pattern_index,
                os.path.basename(path_file)
            ).group()[4:7]
        )
        return index_img

    def paths_to_embeddings(self, dirs_objects, model_embedding, **kwargs):
        """
        Load image paths, calculate embeddings for each image
        and store embeddings with the same sorting as in the input
        directory. Thus, the output variable stores embeddings
        with following structure:
        embeddings_sort_by_objects = {
            object: {
                index: embedding
            }
        }
        """
        # Prepare dictionary to store embeddings
        embeddings_sort_by_objects = dict()

        # Loop through dictionary with object images sorted by objects
        for i, v_object in enumerate(dirs_objects):
            # Prepare object ID
            k_object = pathlib.PurePath(v_object).stem

            # Print info
            print(f'[LOADING][{k_object}] Embeddings for objects '
                  f'{str(i+1).zfill(len(str(len(dirs_objects))))}'
                  f'/{len(dirs_objects)}')

            # Load image paths
            paths_images = self.tools_paths.dir_to_img_paths_expand(
                v_object
            )

            # Load images
            array_images = self.tools_images.fn_images_parse_cv2(
                paths_images)

            # Preprocess images
            array_images = tf.keras.applications.resnet.preprocess_input(array_images)

            # Load embeddings
            embeddings_images = \
                self.tools_embeddings.imgs_to_embeddings(
                    model_embedding,
                    array_images
                )

            # Extract image indices from image paths
            indices_images = [self.fn_index_extract(path_image)
                              for path_image in paths_images]

            # Calculate number of indices
            num_indices = len(indices_images)

            # Extend class variables storing all available indices
            # and numbers of indices by list of image indices for each object
            self.indices_images.extend(indices_images)
            self.num_indices.append(num_indices)

            # Assign embeddings to dictionary storing embeddings
            # by object
            embeddings_sort_by_objects[k_object] = {
                k_index: v_embedding
                for k_index, v_embedding
                in zip(indices_images, embeddings_images)
            }

        # Print info
        print(f'[DONE] Embeddings for timepoint '
              f'{len(dirs_objects)}/{len(dirs_objects)}'
              .ljust(self.format_ljust))
        return embeddings_sort_by_objects


class TNToolsBatchComparisonSimilarities:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This class can be used indirectly by using the class
    'TNToolsBatchComparison' to calculate similarities
    between embeddings of ordered image sequences of multiple
    objects in object batches, e.g. embryos with different
    treatment conditions.
    """
    def __init__(self):
        self.tools_similarities = TNToolsSimilarities()

    def __call__(self,
                 batch_embeddings1,
                 batch_embeddings2):
        """
        Loop through indices in dictionaries of batches of object
        embeddings. For each index and each object embedding in
        each batch, calculate similarities with all object embeddings
        in the second batch.

        Method parameters batch_embeddings1 and batch_embeddings2
        should have the following format:
        {index_img: {object_name: embedding, ...}, ...}.
        """
        # Instantiate dictionaries for similarities at different image indices
        similarities_sequence_batches_1_to_2 = dict()
        similarities_sequence_batches_2_to_1 = dict()

        # Get parameters for looping and printing loop information
        index_max = max(list(batch_embeddings1.keys()))
        len_str_index_max = len(str(index_max))

        # Loop through indices
        for i in range(1, index_max + 1):
            print(f"[INFO][SIMILARITIES] "
                  f"{str(i).zfill(len_str_index_max)}/{index_max}",
                  end="\r")

            # Calculate similarities in both directions
            sims_batch_1_to_2, sims_batch_2_to_1 = \
                self.tools_similarities.cosine_similarities_batches_multiple(
                    batch_embeddings1[i],
                    batch_embeddings2[i]
                )

            # Assign similarities to corresponding dictionaries
            similarities_sequence_batches_1_to_2[i] = sims_batch_1_to_2
            similarities_sequence_batches_2_to_1[i] = sims_batch_2_to_1

        # Make similarity values plottable
        similarities_1_to_2 = \
            self.fn_similarities_dict_to_similarities_plottable(
                similarities_sequence_batches_1_to_2
            )
        mean_1_to_2, std_1_to_2 = \
            self.fn_similarities_dict_to_mean_std_plottable(
                similarities_sequence_batches_1_to_2
            )
        similarities_2_to_1 = \
            self.fn_similarities_dict_to_similarities_plottable(
                similarities_sequence_batches_2_to_1
            )
        mean_2_to_1, std_2_to_1 = \
            self.fn_similarities_dict_to_mean_std_plottable(
                similarities_sequence_batches_2_to_1
            )

        sims_1_to_2 = (similarities_1_to_2, mean_1_to_2, std_1_to_2)
        sims_2_to_1 = (similarities_2_to_1, mean_2_to_1, std_2_to_1)

        return sims_1_to_2, sims_2_to_1

    @staticmethod
    def fn_similarities_dict_to_mean_std_plottable(sims_dict):
        """
        Re-arrange a dict of format {timepoint: {object: similarity}}
        to a list with following format:
        [mean_similarity_timepoint1, mean_similarity_timepoint2, ...]
        """
        mean_plottable = [np.mean(list(_v.values())) for _k, _v in
                          sims_dict.items()]
        std_plottable = [np.std(list(_v.values())) for _k, _v in
                         sims_dict.items()]

        return mean_plottable, std_plottable

    @staticmethod
    def fn_similarities_dict_to_similarities_plottable(sims_dict):
        """
        Re-arrange a dict of format {timepoint: {object: similarity}}
        to a dict with following format:
        {object: [sim_timepoint1, sim_timepoint2, ...]}
        """
        sims_plottable = dict()
        for _k_tp, _v_tp in sims_dict.items():
            for _k_e, _v_e in _v_tp.items():
                if _k_e not in sims_plottable.keys():
                    sims_plottable[_k_e] = list()
                sims_plottable[_k_e].append(_v_e)
        return sims_plottable
