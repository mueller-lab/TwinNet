import matplotlib.pyplot as plt
import random
import re
import tensorflow as tf
import tensorflow_addons as tfa
import tensorflow_io as tfio
from .tngeneral import TNToolsGeneral
from .tninference import TNToolsPaths


class TNToolsTrainingTupletsDataset:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used to prepare tuplets of image paths
    for training of a TN.
    """
    def __init__(self, img_height, img_width, img_height_min, img_width_min, **kwargs):
        self.buffer_size = 1024
        self.format_ljust = 50

        self.img_height = img_height
        self.img_width = img_width
        self.img_height_min = img_height_min
        self.img_width_min = img_width_min
        self.index_limit = 300
        self.index_buffer = 20
        self.index_min = 1
        self.max_index_variation = 20
        self.paths_embryos_experiment_sort = dict()
        self.paths_embryos_total = {'normal_bright_complete': [],
                                    'normal_bright_incomplete': [],
                                    'normal_dark_complete': [],
                                    'normal_dark_incomplete': [],
                                    'exclude_size_complete': [],
                                    'exclude_size_incomplete': [],
                                    'exclude_other_complete': [],
                                    'exclude_other_incomplete': [],
                                    'boom_complete': [],
                                    'boom_incomplete': [],
                                    'dysgenetic_complete': [],
                                    'dysgenetic_incomplete': []}
        self.paths_images_experiment_sort = dict()
        self.paths_images_experiment_sort_selectable_keys = dict()
        self.paths_images_total = {_key: []
                                   for _key
                                   in range(self.index_min,
                                            self.index_limit)}
        self.paths_images_positive = []
        self.paths_images_negative = []
        self.pattern_index = kwargs.get("pattern_index",
                                        "--LO(\d+)")
        self.pattern_index_start = int(kwargs.get("pattern_index_start",
                                                  4))
        self.tools_general = TNToolsGeneral()
        self.tools_paths = TNToolsPaths()
        self.tools_tuplets_images = TNToolsTrainingTupletsImages(img_height,
                                                                 img_width,
                                                                 img_height_min,
                                                                 img_width_min)

    def __call__(self, path_json_train, keys_include, num_samples):
        """
        Prepare tuplets of image paths to use as image triplets
        in a dataset for Twin Network training using Triplet Loss.
        Load paths of embryo directories containing image paths
        from training JSON files. These training JSON files should
        contain directory paths of embryos sorted to the categories
        listed in the class variable 'self.paths_embryos_total'.
        These training JSON files should be listed within a main
        JSON file, the path of which should be given as parameter
        to this method.

        Parameters
        ----------
        path_json_train: str
        keys_include: list
            Keys of embryo types to be included in dataset
        num_samples: int or float
            Number of image path triplets to prepare.

        Returns
        -------
        None.
        """
        self.__init__(self.img_height, self.img_width, self.img_height_min, self.img_width_min)
        self.fn_info('Loading embryo paths', ef='\n')
        self.paths_embryos_load_fn(path_json_train)
        self.fn_info(f'Loading image paths: {*keys_include,}', ef='\n')
        self.paths_images_load_fn(keys_include)
        self.fn_info(f'Checking experiments for empty keys.', ef='\n')
        self.selectable_keys_check()
        self.fn_info(f'Creating {num_samples} image path tuplets', ef='\n')
        self.training_paths_prepare(num_samples)
        self.fn_info(f'Creating datasets', ef='\n')
        dataset = self.dataset_make()
        self.fn_info(f'Dataset cardinality: '
                     f'{tf.data.experimental.cardinality(dataset)}')
        return dataset

    def __len__(self):
        """Number of embryos in dataset."""
        count_embryos_total = 0

        print("\n")
        for key in self.paths_embryos_total.keys():
            print(f"[INFO][{key}]: {len(self.paths_embryos_total[key])}")
            count_embryos_total += len(self.paths_embryos_total[key])

        num_embryos_total = sum(
            len(self.paths_embryos_total[_key])
            for _key in self.paths_embryos_total.keys()
        )
        num_imgs_total = sum(
            len(self.paths_images_total[_key])
            for _key in self.paths_images_total.keys()
        )
        print(f"[INFO][EMBRYOS TOTAL]: {num_embryos_total}",
              )
        print(f"[INFO][IMAGES TOTAL]: {num_imgs_total}",
              )
        return count_embryos_total

    def dataset_make(self):
        """
        Create a tensorflow dataset from image path tuplets.
        """
        dataset_root = tf.data.Dataset.from_tensor_slices(
            self.paths_images_positive
        )
        dataset_positive = tf.data.Dataset.from_tensor_slices(
            self.paths_images_positive
        )
        dataset_negative = tf.data.Dataset.from_tensor_slices(
            self.paths_images_negative
        )
        dataset = tf.data.Dataset.zip((
            dataset_root,
            dataset_positive,
            dataset_negative
        ))

        return dataset

    def fn_indices_sort(self, k_exp, paths_images, slope, intercept):
        """
        For each image file path in a list of image file paths, the
        image index is extracted based on a predefined pattern. For
        each image, the image index is adjusted based on correction
        parameters that are stored in a separate JSON file for each
        experiment. If the corrected image index does not fit the
        index limit, the image is not included in further steps for
        image triplet preparation.

        Parameters
        ----------
        k_exp: str
        paths_images: list
        slope: float
        intercept: float
        """
        self.paths_images_experiment_sort[k_exp] = {
            _key: []
            for _key
            in range(self.index_min,
                     self.index_limit)
        }

        for path_image in paths_images:
            index = int(re.search(self.pattern_index,
                                  path_image).group()[self.pattern_index_start:])
            index_c = round(index * slope + intercept)
            if index_c < self.index_limit:
                self.paths_images_experiment_sort[k_exp][index_c].append(path_image)
                self.paths_images_total[index_c].append(path_image)

    @staticmethod
    def fn_info(string, **kwargs):
        """
        Method to print info text with standardized format.
        """
        print(f'[INFO] {string}',
              end=kwargs.get("ef", ""))

    def fn_key_negative(self, _key_positive, keys_available_negative_max):
        """
        Generate an index key for a negative image based on the following
        three variables:
        - index key of positive image
        - threshold/buffer between index keys of positive and negative images
        - the lower and upper limits for index keys from which a negative image
         may be selected.
        """
        if _key_positive - self.index_buffer <= 0:
            range_key_negative = list(range(
                _key_positive + self.index_buffer,
                keys_available_negative_max - 1
            ))
        elif _key_positive + self.index_buffer >= keys_available_negative_max:
            range_key_negative = list(range(
                self.index_min,
                _key_positive - self.index_buffer
            ))
        else:
            range_key_negative_lower = list(range(
                self.index_min,
                _key_positive - self.index_buffer
            ))
            range_key_negative_upper = list(range(
                _key_positive + self.index_buffer,
                keys_available_negative_max - 1
            ))
            range_key_negative = range_key_negative_lower + range_key_negative_upper
        return range_key_negative

    def fn_paths_imgs_shuffle(self):
        """
        Shuffle paths in self.paths_images_experiment_sort by
        experiment and indices.
        """
        random.seed(1)
        for k_exp in self.paths_images_experiment_sort.keys():
            for index in self.paths_images_experiment_sort[k_exp].keys():
                random.shuffle(self.paths_images_experiment_sort[k_exp][index])

    def paths_embryos_load_fn(self, path_json_train):
        """
        Load the train JSON file. This file should contain paths to the
        experiment JSON files and index correction JSON files, for each
        experiment, to be included in the training. The experiment JSON
        files should contain paths to embryos sorted to the same keys
        as in 'self.paths_embryos_total'. The index correction JSON files
        can be used to adjust for variable acquisition start time points
        and acquisition time intervals in different experiments.

        Parameters
        ----------
        path_json_train: str
        """
        paths_to_files_json_train = self.tools_general.fn_json_load(
            path_json_train
        )

        for v_exp in paths_to_files_json_train:
            json_content_embryos = self.tools_general.fn_json_load(
                paths_to_files_json_train[v_exp][0]
            )
            json_content_correction = self.tools_general.fn_json_load(
                paths_to_files_json_train[v_exp][1]
            )

            slope = json_content_correction['result_regression']['slope']
            intercept = json_content_correction['result_regression']['intercept']

            self.paths_embryos_experiment_sort[v_exp] = {
                _key: [] for _key in self.paths_embryos_total.keys()
            }
            for k_cls in list(
                    self.paths_embryos_experiment_sort[v_exp].keys()):
                for json_content_embryo in json_content_embryos[k_cls]:
                    self.paths_embryos_experiment_sort[v_exp][k_cls].append(
                        [json_content_embryo,
                         slope,
                         intercept]
                    )
                    self.paths_embryos_total[k_cls].append(
                        [json_content_embryo,
                         slope,
                         intercept]
                    )

    def paths_images_load_fn(self, keys_include):
        """
        Load the image file paths of the embryo images stored
        in the embryo directories. While loading the image paths,
        extract the acquisition indices based on the image name.

        Optional: Perform rough index adjustment based on the
        index correction parameters stored with the paths of the
        embryos in the dictionary self.paths_embryos_total.

        Parameters
        ----------
        keys_include: List
            Keys of embryo types to be included in the dataset

        Returns
        -------
        None.
        """
        for k_cls in keys_include:
            n_embs = 0
            for k_exp in self.paths_embryos_experiment_sort.keys():
                for dir_embryo in self.paths_embryos_experiment_sort[k_exp][k_cls]:
                    n_embs += 1
                    print(f'[LOADING] Embryo {n_embs}/'
                          f'{len(self.paths_embryos_total[k_cls])}'
                          .ljust(self.format_ljust),
                          end='\r')
                    path_embryo = dir_embryo[0]
                    paths_images = self.tools_paths.dir_to_img_paths(path_embryo)
                    self.fn_indices_sort(k_exp,
                                         paths_images,
                                         dir_embryo[1],
                                         dir_embryo[2])
            print(f'[DONE] {k_cls} {n_embs}/'
                  f'{len(self.paths_embryos_total[k_cls])}'
                  .ljust(self.format_ljust),
                  end="\n")

        self.fn_paths_imgs_shuffle()
        _ = self.__len__()

    def selectable_keys_check(self):
        """
        Check in the dictionary self.paths_images_experiment_sort
        if all keys have list values containing paths. Update
        self.paths_images_experiment_sort_selectable_keys only
        with the keys for which corresponding values contain image paths.
        """
        for num_experiment in self.paths_images_experiment_sort.keys():
            self.paths_images_experiment_sort_selectable_keys[num_experiment] = \
                sorted([
                    k
                    for k, v
                    in self.paths_images_experiment_sort[num_experiment].items()
                    if len(v) != 0
                ])

    def training_paths_prepare(self, num_samples):
        """
        Generate a specified number of image path pairs for Twin Network training.
        The first image path will be the root image and positive image, the second
        image path will be the negative image. The root image path and negative image
        path will be selected from same the experiment.

        Parameters
        ----------
        num_samples: int
        """
        random.seed(1)
        assert num_samples >= self.index_limit,\
            f'Minimal number of samples: {self.index_limit}'
        num_samples_selected = 0

        while num_samples_selected < num_samples:
            try:
                # Select an experiment
                num_experiment = random.choice(list(
                    self.paths_images_experiment_sort.keys()
                ))
                # Get available index keys
                keys_available_experiment = \
                    self.paths_images_experiment_sort_selectable_keys[num_experiment]

                # Select one index key, from which the anchor and positive image
                # should be selected
                _key_positive = random.choice(
                    keys_available_experiment
                )
                # Get a random image path as anchor and positive image
                path_positive = random.choice(
                    self.paths_images_experiment_sort[num_experiment][_key_positive]
                )

                # Get the highest possible index key for the selected experiment
                keys_available_experiment_max = max(keys_available_experiment)

                # Get the highest index key from which a negative image may
                # be selected
                keys_available_negative_max = min(self.index_limit,
                                                  keys_available_experiment_max)

                # Select a negative image index key
                range_key_negative = self.fn_key_negative(_key_positive,
                                                          keys_available_negative_max)
                _key_negative = random.choice(
                    list(set(keys_available_experiment) & set(range_key_negative))
                )

                # Get a random image path as negative image from the
                # negative image index key
                path_negative = random.choice(
                    self.paths_images_experiment_sort[num_experiment][_key_negative]
                )

                # Store paths of anchor/positive and negative images in containers
                self.paths_images_positive.append(path_positive.replace('\\', '/'))
                self.paths_images_negative.append(path_negative.replace('\\', '/'))

                num_samples_selected += 1
            except IndexError:
                pass
        assert len(self.paths_images_positive) == len(self.paths_images_negative),\
            'Unequal number of images.'


class TNToolsTrainingTupletsImages:

    def __init__(self, img_height, img_width, img_height_min, img_width_min):
        self.img_height = img_height
        self.img_width = img_width
        self.img_height_min = img_height_min
        self.img_width_min = img_width_min

    def image_parse_fn(self, path_img, **kwargs):
        """Load image from path."""
        img = tf.io.read_file(path_img)
        img = tfio.experimental.image.decode_tiff(img)
        img = tf.cast(img, tf.float32)
        if 'rotation' in kwargs:
            img = tfa.image.rotate(img, kwargs['rotation'])
        img = tf.image.resize_with_crop_or_pad(img,
                                               self.img_height_min,
                                               self.img_width_min)
        img = tf.image.resize(img, (self.img_height, self.img_width))
        img = tf.reshape(img, (self.img_height, self.img_width, 4))
        img = tfio.experimental.color.rgba_to_rgb(img)
        return img

    def images_parse_fn(self, path_root, path_positive, path_negative):
        """
        Load root image and negative image. Use rotation of root image
        as positive image.
        """
        angle = tf.random.uniform(shape=[1],
                                  minval=0,
                                  maxval=360,
                                  dtype=tf.float32)

        img_root = self.image_parse_fn(path_root)
        img_positive = self.image_parse_fn(path_positive, rotation=angle)
        img_negative = self.image_parse_fn(path_negative, rotation=angle)
        return img_root, img_positive, img_negative

    @staticmethod
    def visualize(img_root, img_positive, img_negative):
        """Visualize three triplets from the supplied batches."""

        def show(ax, image):
            ax.imshow(image / 255, cmap='gray')
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)

        fig = plt.figure(figsize=(9, 9))

        axs = fig.subplots(3, 3)
        for i in range(3):
            show(axs[0, i], img_root[i])
            show(axs[1, i], img_positive[i])
            show(axs[2, i], img_negative[i])
