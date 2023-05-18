import itertools
import numpy as np
import pandas as pd
import pathlib
import re
from scipy.stats import zscore
import time

from .tninference import TNToolsEmbeddings
from .tninference import TNToolsPaths
from .tninference import TNToolsSimilarities


class TNToolsDeviationInBatch:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    for evaluation purposes. This part of the toolset is used for the
    detection of deviation from normal development based on similarity
    values calculated between test objects, e.g. embryos, in on batch.
    """
    def __init__(self):
        self.embeddings_objects = dict()
        self.embeddings_objects_ordered = dict()
        self.format_ljust = 50

        self.num_imgs = list()
        self.num_imgs_max = 0
        self.num_objects = 0
        self.num_objects_include = 0

        self.paths_objects_images = dict()
        self.paths_objects_images_include = dict()

        self.pattern_index = '--LO(.*)--CO'

        self.similarities_objects = pd.DataFrame()
        self.similarities_objects_cumulative = None

        self.tools_embeddings = TNToolsEmbeddings(size_img=224,
                                                  size_img_min=300)
        self.tools_paths = TNToolsPaths()
        self.tools_similarities = TNToolsSimilarities()

        self.zscores_objects = None
        self.zscores_objects_cumulative = None

    def __call__(self, paths_dirs_objects, model_embedding, **kwargs):
        """
        Assess if individual objects in a batch of test objects,
        e.g. embryos, show deviations from normal development
        based on similarity calculation between all objects in
        one batch.
        For this, load images for each test object, calculate
        embeddings using Twin Network, and calculate similarities.

        Parameters
        ----------
        paths_dirs_objects: list
            Provide list of separated directory paths for each
            object in the test batch containing an image sequence
            of the object.
        model_embedding: keras.engine.functional.Functional
            Embedding model of Twin Network.
        **kwargs: variable keyword arguments
            See below.

        Keyword arguments
        -----------------
        limit: int
        filetype_expand: boolean

        """
        # Track duration
        st = time.time()
        # Reset variables if class was called previously
        self.__init__()
        # Load image paths
        self.dataset_paths_complete_get(paths_dirs_objects)
        # Exclude object detections if necessary
        self.dataset_paths_select(**kwargs)
        # Print info about dataset
        self.dataset_stats_print()
        # Calculate embeddings for all images per object
        self.dataset_embeddings_calc(model_embedding)
        # Sort embeddings by indices stored in image file names
        self.embeddings_sort()
        # Calculate similarities
        self.embeddings_to_similarities()
        # Calculate cumulative sums and z-scores
        self.similarities_to_cumsums_zscores()

        print(f"[INFO][DURATION] {time.time()-st:.2f}s".
              ljust(self.format_ljust))

        return self.similarities_objects

    def dataset_embeddings_calc(self, model_embedding, **kwargs):
        """
        After loading ordered image paths for each object,
        calculate embeddings and return them sorted by
        objects and image file names.

        Keyword arguments
        -----------------
        filetype_expand: boolean
            Indicate if image files of other file type than '.tif'
            should be loaded. Default is False.
        """
        num_embeddings_done = 1
        # For formatting of info which is printed during embedding calculation
        num_zeros = len(str(self.num_objects_include))
        # Loop through dictionary with keys/values of
        # object directory name/ image path list
        for k, v in self.paths_objects_images_include.items():
            print(f"[INFO][EMBEDDINGS] "
                  f"{str(num_embeddings_done).zfill(num_zeros)}/"
                  f"{self.num_objects_include}".ljust(self.format_ljust),
                  end="\r")
            self.embeddings_objects[k] = self.tools_embeddings.\
                list_to_embeddings_keep_order(v,
                                              model_embedding,
                                              **kwargs)
            num_embeddings_done += 1

    def dataset_paths_complete_get(self, paths_dirs_objects, **kwargs):
        """
        Method to answer the following questions:
        1. How many objects/embryos are in the dataset?
        2. How many images does each object have?
        3. Are there objects with fewer images compared to other objects?

        Parameters
        ----------
        paths_dirs_objects: list
        kwargs: Variable keyword arguments
            See below.

        Keyword arguments
        -----------------
        filetype_expand: boolean
            Indicate if image files of other file type than '.tif'
            should be loaded. Default is False.

        Returns
        -------
        None.
        """
        for path_dir_object in paths_dirs_objects:
            name_object = pathlib.PurePath(path_dir_object).stem
            if kwargs.get("filetype_expand", False):
                paths_imgs = self.tools_paths.dir_to_img_paths_expand(
                    path_dir_object
                )
            else:
                paths_imgs = self.tools_paths.dir_to_img_paths(
                    path_dir_object
                )
            self.paths_objects_images[name_object] = paths_imgs
            self.num_imgs.append(len(paths_imgs))
        self.num_objects = len(self.paths_objects_images.keys())

    def dataset_paths_select(self, **kwargs):
        """
        Select only paths of objects that each have at least 80 %
        of the max number of images in the dataset. Alternatively,
        specify the minimum number of images per object to include
        in the analysis, starting with the first image in the sequence.
        """
        # What is the maximum number of images in the dataset?
        self.num_imgs_max = max(self.num_imgs)
        # Get the minimum number of images for objects to be
        # included in the analysis
        limit = kwargs.get('limit',
                           round(0.8 * self.num_imgs_max))
        self.paths_objects_images_include = {
            k: v
            for k, v in self.paths_objects_images.items()
            if len(v) >= limit
        }
        self.num_objects_include = len(
            self.paths_objects_images_include.keys())

    def dataset_stats_print(self):
        """
        Print info about objects after sorting.
        """
        for k, v in self.paths_objects_images.items():
            if k in self.paths_objects_images_include.keys():
                base_str_info = f"[INFO][OK] Object"
            else:
                base_str_info = f"[INFO][DISCARD] Object"
            print(f"{base_str_info} {k}: {len(v)} images.",
                  end='\n')

    def embeddings_sort(self):
        """
        Change sorting of embeddings in 'self.embeddings_objects' from
        {object_name: {img_name: embedding, ...}, ...}
        to
        {index_img: {object_name: embedding, ...}, ...}.
        """
        for k_emb, v_emb in self.embeddings_objects.items():
            for k_name, v_name in v_emb.items():
                idx = int(re.search(self.pattern_index, k_name).group()[4:7])
                if idx not in self.embeddings_objects_ordered.keys():
                    self.embeddings_objects_ordered[idx] = dict()
                self.embeddings_objects_ordered[idx][k_emb] = v_name

    def embeddings_to_similarities(self):
        """
        Calculate cosine similarities between model-generated embeddings.
        For each index in self.embeddings_objects_ordered, similarities
        between embeddings of all objects are calculated.
        """
        # Loop through indices of ordered batches of embeddings
        for k_idx, v_idx in self.embeddings_objects_ordered.items():
            # Get list of object names in batch at index
            keys_objects_idx = list(v_idx.keys())
            num_objects_idx = len(keys_objects_idx)

            # Get combinations of object name keys
            combinations = list(itertools.combinations(keys_objects_idx, 2))

            # Create a template pandas.core.series.Series object
            sims_objects_index = pd.Series(
                data={v_obj: 0 for v_obj in keys_objects_idx},
                dtype=np.float64,
                index=keys_objects_idx,
                name=k_idx
            )

            # Print info
            print(f"[LOADING][SIMILARITIES] "
                  f"{k_idx}/{self.num_imgs_max} "
                  f"{len(combinations)}".ljust(50),
                  end="\r")

            # Loop through combinations and calculate similarities
            # of object embeddings
            for k_obj1, k_obj2 in combinations:
                # Calculate similarity for combination of objects
                sim = self.tools_similarities.fn_cosine_similarity(
                    v_idx[k_obj1], v_idx[k_obj2]
                )

                # Assign similarities to pandas.core.series.Series
                sims_objects_index[k_obj1] += sim / (num_objects_idx - 1)
                sims_objects_index[k_obj2] += sim / (num_objects_idx - 1)

            # Concatenate similarities of batch at index to
            # dataframe with index similarities at all image indices
            self.similarities_objects = pd.concat(
                [self.similarities_objects,
                 sims_objects_index.to_frame().T]
            )

        # Print info
        print(f"[DONE][SIMILARITIES] "
              f"{self.num_imgs_max}/{self.num_imgs_max}".ljust(50),
              end="\n")

    def similarities_to_cumsums_zscores(self, **kwargs):
        """
        Convenience method to calculate cumulative sums and z-scores
        for similarities of batch at different indices.
        """
        similarities = kwargs.get("similarities", self.similarities_objects)
        self.similarities_objects_cumulative = similarities.cumsum()
        self.zscores_objects = similarities.apply(zscore, axis=1)
        self.zscores_objects_cumulative = similarities.\
            apply(zscore, axis=1).cumsum()
