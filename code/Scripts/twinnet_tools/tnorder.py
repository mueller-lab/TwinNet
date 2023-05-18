import glob
import itertools
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
import random
import re
import scipy.stats as ss
import sys
import tensorflow as tf
import tensorflow_io as tfio
from tensorflow.keras import applications, layers, models

sys.path.append('D:/Deep_learning_3/00_Siamese_scripts/')

from .tninference import TNToolsEmbeddings


new_rc_params = {'text.usetex': False,
                 'svg.fonttype': 'none',
                 'lines.linewidth': 1}

matplotlib.rcParams.update(new_rc_params)


class OrderTemporalSequenceTN:
    """
    A class to calculate the order of a sequence
    of image embeddings, e.g. of zebrafish embryos,
    that are previously sorted in a random order.

    Here, we try to assign each index a succeeding index,
    first based on the highest similarity value, however
    if that is not available based on the second, third,
    etc. highest similarity value.
    """
    def __init__(self, array_input):
        print(f'[INFO] Number of {len(array_input[0])}' +
              f'-dimensional arrays: {len(array_input)}')

        self.array_input = array_input
        self.num_input = len(array_input)

        self.eds = np.zeros((self.num_input, self.num_input))
        self.css = np.zeros((self.num_input, self.num_input))

        self.eds_zscores = np.zeros((self.num_input, self.num_input))
        self.css_zscores = np.zeros((self.num_input, self.num_input))
        self.sum_zscores = np.zeros((self.num_input, self.num_input))

        self.indices_avail = list(range(self.num_input))

        self.ljust = 50

    def __call__(self):
        """Ordering input arrays based on similarity values."""
        # Step 1: Calculate similarities and store in
        # matrices (numpy.ndarrays)
        self.similarities_embeddings_calculate()
        # Step 2: Calculate z-scores for each row
        # of embedding similarity values.
        self.zscores_calculate()
        # Step 3: Check how high the sum of z-scores
        # would be when starting at different rows.
        indices_ordered = self.indices_loop()

        return indices_ordered

    @staticmethod
    def fn_indices_sim_nth_highest(values_row, nth_value):
        """
        Get the index with n-highest similarity
        value, with n given by 'nth_value'.
        """
        # This creates a list of indices for which
        # the corresponding values are sorted from
        # low to high. From this list we take the
        # nth element corresponding to the nth
        # highest value (for cosine similarities).
        index_next = values_row.argsort()[-nth_value]

        return index_next

    def fn_cosine_similarity(self, index_a, index_b):
        """
        Calculate cosine similarity between two values
        of input array at index_a and index_b.
        """
        a = np.squeeze(self.array_input[index_a])
        b = np.squeeze(self.array_input[index_b])
        cs = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        self.css[index_a][index_b] = cs
        self.css[index_b][index_a] = cs

    def fn_euclidian_distance(self, index_a, index_b):
        """Calculate euclidian distance between two given inputs."""
        ed = np.linalg.norm(
            self.array_input[index_a] - self.array_input[index_b]
        )
        self.eds[index_a][index_b] = ed
        self.eds[index_b][index_a] = ed

    def fn_indices_loop_argmax(self, index_start):
        """
        Based on the start index, loop through the embeddings
        by following the index of the highest zscore value.
        Every time a connection was made drop index from
        list of available indices.
        """
        indices_ordered = [index_start]
        indices_avail = self.indices_avail.copy()
        indices_avail.remove(index_start)
        sum_zscores = 0
        num_nonmax = 0

        while len(indices_avail) != 0:
            # Get values of start row
            values_row = self.sum_zscores[index_start]

            # Get column index, corresponding to row, of
            # lowest z-score
            index_next = np.argmax(values_row)

            # If index with lowest z-score is available,
            # just continue and append
            if index_next in indices_avail:
                pass
                # print(f'Found direct next index {index_next}.')

            # If index with the highest similarity is not available
            else:
                num_nonmax += 1
                # Check if the indices with next highest similarities
                # are available.
                nth_value = 2
                index_found = None
                while index_found is None:
                    # Get index with next highest similarity
                    index_next = self.fn_indices_sim_nth_highest(values_row,
                                                                 nth_value)

                    # Is next index available?
                    if index_next in indices_avail:
                        index_found = True
                    else:
                        # Increase search radius by 1
                        nth_value += 1

            sum_zscores += values_row[index_next]
            indices_ordered.append(index_next)
            indices_avail.remove(index_next)
            index_start = index_next

        return {"idx_ordered": indices_ordered,
                "sum_zscores": sum_zscores,
                "num_nonmax": num_nonmax}

    def fn_values_contrast(self, index):
        """
        Calculate z-score for value per row (set of similarities)
        of the similarity arrays.
        """
        values_ed = self.eds[index]
        mean_ed, std_ed = np.mean(values_ed), np.std(values_ed)
        z_scores_ed = np.apply_along_axis(self.fn_zscore, 0,
                                          values_ed, mean_ed, std_ed)
        self.eds_zscores[index] = z_scores_ed

        values_cs = self.css[index]
        mean_cs, std_cs = np.mean(values_cs), np.std(values_cs)
        z_scores_cs = np.apply_along_axis(self.fn_zscore, 0,
                                          values_cs, mean_cs, std_cs)
        self.css_zscores[index] = z_scores_cs

    @staticmethod
    def fn_zscore(value, mean, std):
        """
        Calculate a z-score for a combination of
        value, mean and standard deviation.
        """
        return (value - mean) / std

    def indices_loop(self):
        """
        Loop through the embeddings by following
        the index of the highest similarity value.
        Perform such looping starting at each row.
        After this step, assign the following values
        for each starting row to a dictionary:

        - key: starting row index (beginning with 0)
        - values:
            "idx_ordered": list of ordered indices
            "sum_sims": sum of similarity values
            "num_nonmax": number of times that the
                          highest similarity value
                          could not be assigned
        """
        indices_ordered = dict()

        for i in range(self.num_input):
            print(f'[LOADING][Orderings] {str(i + 1).zfill(4)}/'
                  f'{str(self.num_input).zfill(4)}'.ljust(self.ljust),
                  end='\r')
            indices_ordered[i] = self.fn_indices_loop_argmax(i)

        print(f'[DONE][Orderings] {str(self.num_input).zfill(4)}/'
              f'{str(self.num_input).zfill(4)}'.ljust(self.ljust))

        return indices_ordered

    def similarities_embeddings_calculate(self):
        """
        This function takes n embedding arrays as an input,
        combines the embeddings and calculates similarities
        based on Euclidian distance and cosine similarity.

        Similarities are stored in numpy arrays based on the
        embedding indices.
        """
        combinations = list(itertools.combinations(list(range(len(self.array_input))), 2))
        combinations = [(a, b) for (a, b) in combinations if a != b]

        for i in range(len(combinations)):
            if not i % 100:
                print(f'[LOADING][Similarities] {str(i).zfill(4)}/'
                      f'{str(len(combinations)).zfill(4)}'.ljust(self.ljust), end='\r')
            self.fn_cosine_similarity(combinations[i][0], combinations[i][1])
            self.fn_euclidian_distance(combinations[i][0], combinations[i][1])
        print(f'[DONE][Similarities] {str(len(combinations)).zfill(4)}/'
              f'{str(len(combinations)).zfill(4)}'.ljust(self.ljust))
        # After completing the similarity calculations, all
        # combinations of embeddings are assigned similarity values.
        # However, in the arrays of similarity values the
        # 'self-comparisons' are missing similarity values and have
        # the original value '0'. This can later lead to incorrect
        # ordering, so we assign the mean similarity value
        # found in each row of Euclidian distances and
        # cosine similarities to the respective 'self-comparison'.
        indices_self_comparisons = list(range(len(self.array_input)))

        for i in indices_self_comparisons:
            self.eds[i, i] = np.mean(self.eds[i])
            self.css[i, i] = np.mean(self.css[i])

    def zscores_calculate(self):
        """
        Calculate z-scores for Euclidian distance
        and Cosine similarity values. If the score
        is high, predicted positions can already be
        assigned in a next step.
        """
        for _i in range(self.num_input):
            self.fn_values_contrast(_i)
        self.sum_zscores = self.css_zscores + (-1) * self.eds_zscores


class DataInferenceTemporalSequenceTN:
    """
    A class to load and handle data for image
    sequence ordering with Twin Network.
    """
    def __init__(self):
        self.img_size_min = 300
        self.img_size = 224
        self.tools_embeddings = TNToolsEmbeddings(self.img_size,
                                                  self.img_size_min)

    @staticmethod
    def fn_fit_linear(values_x, values_y):
        """
        Fit linear regression model for image ordering
        data and return True if slope is negative.
        """
        m = np.polyfit(values_x, values_y, 1)
        if m[0] < 0:
            return True
        else:
            return False

    def fn_image_tiff_parse(self, path_img):
        """Load TIFF image from path."""
        img1 = tf.io.read_file(path_img)
        img2 = tfio.experimental.image.decode_tiff(img1)
        img3 = tf.image.resize_with_crop_or_pad(img2,
                                                self.img_size_min,
                                                self.img_size_min)
        img4 = tf.reshape(img3, (self.img_size_min,
                                 self.img_size_min, 4))
        img5 = tf.image.resize(img4, (self.img_size,
                                      self.img_size))
        img6 = tfio.experimental.color.rgba_to_rgb(img5)
        img7 = tf.keras.applications.resnet50.preprocess_input(img6)
        return img7

    def fn_images_tiff_parse(self, paths_images):
        """
        Load multiple tiff images from paths
        to a numpy.ndarray with tfio.
        """
        image_segments = list()
        num_images = len(paths_images)

        for i in range(num_images):
            print(f'[LOADING][Images] {str(i + 1).zfill(4)}/'
                  f'{str(num_images).zfill(4)} ...'.ljust(50),
                  end='\r')
            path_image = paths_images[i]

            image_segment = self.fn_image_tiff_parse(path_image)
            image_segments.append(image_segment)
        print(f'[DONE][Images] {str(num_images).zfill(4)}/'
              f'{str(num_images).zfill(4)}'.ljust(50))

        return np.array(image_segments)

    @staticmethod
    def fn_indices_reverse(indices_decoded, idxs_order_reference, **kwargs):
        if kwargs.get('reverse_test', False):
            indices_decoded = list(reversed(indices_decoded))
        if kwargs.get('reverse_reference', False):
            idxs_order_reference = list(reversed(idxs_order_reference))
        return indices_decoded, idxs_order_reference

    @staticmethod
    def fn_json_load(path_json):
        """Load json file."""
        with open(path_json, 'rb') as JsonFile:
            content = json.load(JsonFile)
        return content

    @staticmethod
    def fn_handle_plot_older_version(path_save):
        """
        When trying to save a plot, this function checks
        if a previous version of the respective plot is
        already saved under the specified path. If so,
        rename the previous plot to _VX, X standing for
        version number, and return the newest name.
        """
        p = pathlib.PurePath(path_save)
        d = p.parent
        n = p.stem

        if re.search(r'[V]\d{3}.svg$', path_save):
            n_stem_blank = f'{str(n)[:-5]}'
        else:
            n_stem_blank = n

        versions_previous = list(sorted(glob.glob(os.path.join(str(d), f'{n_stem_blank}*.*'))))
        if len(versions_previous) != 0:
            version_last_path = versions_previous[-1]
            version_last_id = int(str(pathlib.PurePath(version_last_path).stem)[-3:])
            version_new_id = version_last_id + 1
        else:
            version_new_id = 1

        path_save = os.path.join(str(d), f'{n_stem_blank}_V{str(version_new_id).zfill(3)}')

        return path_save

    @staticmethod
    def fn_textfile_read(path_text):
        """
        Read a text file containing only numbers
        and return content as list of integers.
        """
        with open(path_text, 'r') as textfile:
            content = textfile.read()
        indices_reference = [int(a) for a in content.split('\n') if a != '']
        # For fairness of comparison, images can be reordered
        # in a way that the first image is the known first image
        # of the sequence
        # index_start = indices_reference.index(1)  # Matlab indexing starts with 1
        # indices_reference = indices_reference[index_start:] + \
        #    indices_reference[:index_start]
        return indices_reference

    @staticmethod
    def embedding_make():
        """
        Load modified ResNet50 architecture.
        """
        base_cnn = applications.resnet.ResNet50(
            weights="imagenet", input_shape=(224, 224, 3), include_top=False
        )

        flatten = layers.Flatten()(base_cnn.output)
        dense1 = layers.Dense(512, activation="relu")(flatten)
        dense1 = layers.BatchNormalization()(dense1)
        dense2 = layers.Dense(256, activation="relu")(dense1)
        dense2 = layers.BatchNormalization()(dense2)
        output = layers.Dense(256)(dense2)

        embedding = models.Model(base_cnn.input, output, name="Embedding")

        trainable = False
        for layer in base_cnn.layers:
            if layer.name == "conv5_block1_out":
                trainable = True
            layer.trainable = trainable

        return embedding

    @staticmethod
    def deviation_temporal_average_calculate(indices_decoded, idxs_order_reference,
                                             num_imgs_total, size_step):
        """
        Calculate the average temporal deviation from the true
        image ordering for both the TN predicted image order
        (indices given by 'indices_decoded') and the image
        order predicted by Dsilva et al. 2015 method
        (as given by idxs_order_reference).

        Parameters
        ----------
        indices_decoded: list
            Indices of image paths ordered based on prediction
            of TN.
        idxs_order_reference: list
            Indices of image paths ordered based on prediction
            of Dsilva et al. 2015 method.
        num_imgs_total: int
            Number of images in experiment.
        size_step: int
            The ratio at which images were drawn from the
            full dataset, e.g., "2" if every 2nd image was
            used in the current analysis.
        """
        # True values
        order_true = list(range(0, num_imgs_total, size_step))

        deviation_tn = [abs(a * size_step - b) for a, b in zip(indices_decoded, order_true)]
        deviation_ref = [abs(a * size_step - b) for a, b in zip(idxs_order_reference, order_true)]

        return deviation_tn, deviation_ref

    def indices_reference_load(self, path_vals_reference):
        """
        Load reference indices as predicted by the method of Dsilva et al. 2015.

        These reference images are values which are ordered by the predicted
        image order, and each value corresponds to the original image index.
        """
        idxs_order_reference = self.fn_textfile_read(path_vals_reference)
        return idxs_order_reference

    def list_to_embeddings(self, list_embryos_images, model_embedding):
        """Generate embeddings for a set of embryo images."""
        self.__init__()
        array_imgs = self.fn_images_tiff_parse(list_embryos_images)
        embeds_imgs = self.tools_embeddings.imgs_to_embeddings(model_embedding,
                                                               array_imgs)
        return embeds_imgs

    @staticmethod
    def temporal_ordering_derivation(idxs_order_pred, idxs_order_ref):
        """
        Takes a list of original indices ordered by either
        TN prediction or reference prediction and returns
        the change of original index values, as "derivation"
        at each frame number.
        """
        deriv_order_pred = list()
        deriv_order_ref = list()

        for i in range(1, len(idxs_order_pred)):
            deriv_order_pred.append(abs(idxs_order_pred[i] - idxs_order_pred[i - 1]))

        for i in range(1, len(idxs_order_ref)):
            deriv_order_ref.append(abs(idxs_order_ref[i] - idxs_order_ref[i - 1]))

        return deriv_order_pred, deriv_order_ref

    @staticmethod
    def test_significance(samples):
        """
        Test significance of difference in central tendencies
        for dependent samples on ordering results, both for
        absolute values and for values adjusted for frame count.
        """
        # Original values
        print('ORIGINAL SAMPLES')
        samples_tn = [np.mean(_v[0]) for _v in samples.values()]
        samples_ref = [np.mean(_v[1]) for _v in samples.values()]

        # Are samples normally distributed?
        norm_res_tn = ss.kstest(samples_tn, 'norm')
        norm_res_ss = ss.kstest(samples_ref, 'norm')
        if norm_res_tn.pvalue < 0.05 or norm_res_ss.pvalue < 0.05:
            res = ss.wilcoxon(samples_tn, samples_ref)
            print(f'Test result non-normal-distribution: '
                  f'{res}')
        else:
            res = ss.ttest_rel(samples_tn, samples_ref)
            print(f'Test result normal-distribution: '
                  f'{res}')

        # Normalized values
        print('NORMALIZED SAMPLES')
        samples_tn_norm = [np.mean(_v[0]) / len(_v[0])
                           for _v in samples.values()]
        samples_ref_norm = [np.mean(_v[1]) / len(_v[0])
                            for _v in samples.values()]

        # Are samples normally distributed?
        norm_res_tn = ss.kstest(samples_tn_norm, 'norm')
        norm_res_ss = ss.kstest(samples_ref_norm, 'norm')
        if norm_res_tn.pvalue < 0.05 or norm_res_ss.pvalue < 0.05:
            res = ss.wilcoxon(samples_tn_norm, samples_ref_norm)
            print(f'Test result non-normal-distribution: '
                  f'{res}')
        else:
            res = ss.ttest_rel(samples_tn_norm, samples_ref_norm)
            print(f'Test result normal-distribution: '
                  f'{res}')
        return res


class PlotTemporalSequenceTN:
    """
    A class to display the order of a sequence
    of image embeddings, e.g. of zebrafish embryos,
    that were previously sorted in a random order,
    as predicted with Twin Networks and with reference
    method from Dsilva et al. 2015 method.
    """
    def __init__(self):
        self.plot_alpha_bg = 0.5
        self.plot_alpha_fg = 1
        self.plot_color_groundtruth = "#1e9b8a"
        self.plot_color_refmeth = "#f57f20"
        self.plot_color_tn = "#2378b5"
        self.plot_fontsize_large = 8
        self.plot_fontsize_small = 6
        self.plot_linestyle = '-'
        self.plot_linewidth = 1
        self.plot_marker = 'o'
        self.plot_markersize = self.plot_linewidth * 2

    @staticmethod
    def fn_color_get(num_clusters, num_cluster):
        """
        Get color value from colormap.
        """
        cmap = matplotlib.cm.get_cmap('Spectral')
        return cmap(1 / num_clusters * num_cluster)

    def plot_ordering_sims_breakpoints(self, idxs_ordered, idxs_order_reference,
                                       values_breaks,
                                       size_step, num_imgs_total, **kwargs):
        """
        Plot results of usage of TN for ordering.
        """
        # Plot figure
        fig, ax = plt.subplots(1, figsize=(10, 5), dpi=300)

        x_values_plot = list(range(0, num_imgs_total, size_step))
        # Necessary because indices are smaller for larger
        # step sizes while overall length is still the same
        values_adjusted_size_step = [a * size_step for a in idxs_ordered]

        # Predictions
        ax.plot(x_values_plot,
                values_adjusted_size_step,
                marker=self.marker,
                ls=self.linestyle)

        # Similarity breaks
        x_values_sims_breaks = values_breaks
        y_values_sims_breaks = [100] * len(x_values_sims_breaks)

        ax.scatter(x_values_sims_breaks,
                   y_values_sims_breaks,
                   marker='o',
                   c='red')
        ax.set_title(kwargs.get('title', f'Predicted image ordering'))

        # Other plots
        # Ground truth
        ground_truth_x = x_values_plot
        ground_truth_y = x_values_plot
        ax.plot(ground_truth_x, ground_truth_y, c='darkgreen',
                label='Ground truth')

        # Reference
        plt.plot(x_values_plot,
                 [a * size_step for a in idxs_order_reference],
                 label='Dsilva et al. based order',
                 marker=self.marker,
                 ls=self.linestyle)

        # Adjust plot parameters
        ax.set_xlabel(kwargs.get('title', 'Predicted frame indices'))
        ax.set_ylabel('True indices from image timeseries')
        plt.legend()
        if kwargs.get('savefig', False):
            plt.savefig(kwargs.get('savefig'))
        else:
            plt.show()
        plt.close()

    def plot_ordering(self, idxs_ordered, idxs_order_reference,
                      size_step, num_imgs_total,
                      **kwargs):
        """
        Plot results of usage of TN for image ordering.
        """
        # Plot figure
        fig, ax = plt.subplots(1, figsize=(5, 3), dpi=300)

        x_values_plot = list(range(0, num_imgs_total, size_step))

        # Necessary because indices are smaller for larger
        # step sizes while overall length is still the same
        values_adjusted_size_step = [a * size_step for a in idxs_ordered]
        # Predictions
        ax.plot(x_values_plot,
                values_adjusted_size_step,
                alpha=self.plot_alpha_fg,
                color=self.plot_color_tn,
                ls=self.plot_linestyle,
                lw=self.plot_linewidth,
                marker=self.plot_marker,
                markersize=1)

        # Ground truth
        ground_truth_x = x_values_plot
        ground_truth_y = x_values_plot
        ax.plot(ground_truth_x, ground_truth_y, c='darkgreen',
                alpha=self.plot_alpha_fg,
                label='Ground truth')

        # Reference
        plt.plot(x_values_plot,
                 [a * size_step for a in idxs_order_reference],
                 alpha=self.plot_alpha_fg,
                 color=self.plot_color_refmeth,
                 ls=self.plot_linestyle,
                 lw=self.plot_linewidth,
                 marker=self.plot_marker,
                 markersize=1)

        # Adjust plot parameters
        ax.set_xlabel(kwargs.get('title', 'Predicted ordering'),
                      fontsize=self.plot_fontsize_large)
        ax.set_ylabel('Indices from image time series',
                      fontsize=self.plot_fontsize_large)
        ax.tick_params(axis='both', which='both',
                       labelsize=self.plot_fontsize_small)
        if kwargs.get('savefig', False):
            plt.savefig(kwargs.get('savefig'))
        else:
            plt.show()
        plt.close()

    def deviation_avg_plot(self, deviations_embryo, total_length, **kwargs):
        """
        Plot average deviations from ground truth for
        TN predicted ordering and Dsilva et al. 2015 method.
        """
        sizes_step = [1, 2, 3, 4, 5, 10, 20]
        dataset_lengths = [int(total_length / s_step)
                           for s_step in sizes_step]
        share_number_test_images = [
            f'{round(total_length / s_step / total_length * 100, 1)}'
            for s_step in sizes_step
        ]

        fig, ax = plt.subplots(1, figsize=(5, 3), dpi=300)

        if kwargs.get('absolute', True):
            ax.plot([np.mean(_v[0]) for _v in deviations_embryo.values()],
                    alpha=self.plot_alpha_fg,
                    color=self.plot_color_tn,
                    ls=self.plot_linestyle,
                    lw=self.plot_linewidth,
                    marker=self.plot_marker,
                    markersize=1)

            # Reference
            ax.plot([np.mean(_v[1]) for _v in deviations_embryo.values()],
                    alpha=self.plot_alpha_fg,
                    color=self.plot_color_refmeth,
                    ls=self.plot_linestyle,
                    lw=self.plot_linewidth,
                    marker=self.plot_marker,
                    markersize=1)
            ax.set_ylabel('Deviation \n [Number of frames]')
        else:
            ax.plot([np.mean(_v[0]) / dl
                    for _v, dl in zip(deviations_embryo.values(),
                                      dataset_lengths)],
                    alpha=self.plot_alpha_fg,
                    color=self.plot_color_tn,
                    ls=self.plot_linestyle,
                    lw=self.plot_linewidth,
                    marker=self.plot_marker,
                    markersize=1)

            # Reference
            ax.plot([np.mean(_v[1]) / dl
                     for _v, dl in zip(deviations_embryo.values(),
                                       dataset_lengths)],
                    alpha=self.plot_alpha_fg,
                    color=self.plot_color_refmeth,
                    ls=self.plot_linestyle,
                    lw=self.plot_linewidth,
                    marker=self.plot_marker,
                    markersize=1)
            ax.set_ylabel('Deviation \n'
                          '[Number of frames/number of frames in dataset]')

        ax.set_xticks(range(len(sizes_step)), share_number_test_images)
        ax.set_xlabel('Percentage of frame count of original experiment [%]')
        plt.tight_layout()
        if kwargs.get('savefig', False):
            plt.savefig(kwargs.get('savefig'))
        else:
            plt.show()
        plt.close()

    @staticmethod
    def derivation_plot(deriv_order_pred, deriv_order_ref, total_length, size_step, **kwargs):
        """
        Plot index changes for temporal image ordering
        predictions of TN method and reference method.
        """
        # Plot figure
        fig, ax = plt.subplots(1, 1, figsize=(10, 5), dpi=300)

        # Predictions
        ax.plot(range(0, total_length - 1, size_step),
                deriv_order_pred,
                label='TN predicted order')

        ax.set_title(f'Predicted image ordering')

        # Ground truth
        ground_truth_x = list(range(0, total_length - 1, size_step))
        ground_truth_y = [1] * (total_length - 1)

        ax.plot(ground_truth_x, ground_truth_y, c='darkgreen',
                label='Ground truth')

        # Reference
        plt.plot(range(0, total_length - 1, size_step),
                 deriv_order_ref,
                 label='Dsilva et al. based order')

        # Adjust plot parameters
        ax.set_xlabel('Predicted frame indices')
        ax.set_ylabel('True indices from image timeseries')
        plt.legend()
        if kwargs.get('savefig', False):
            plt.savefig(kwargs.get('savefig'))
        else:
            plt.show()
        plt.close()

    @staticmethod
    def derivation_mean_plot(deriv_orders, total_length, **kwargs):
        """
        Plot index changes for temporal image ordering
        predictions of TN method and reference method.
        """
        sizes_step = [1, 2, 3, 4, 5, 10, 20]
        dataset_lengths = [int(total_length / s_step) for s_step in sizes_step]
        share_number_test_images = [f'{round(total_length / s_step / total_length * 100, 1)}' for s_step in sizes_step]
        fig, ax = plt.subplots(2, 1, figsize=(10, 10), dpi=300, sharex='col')

        ax[0].plot([np.mean(_v[0]) for _v in deriv_orders.values()], label='TN method', marker='o')
        ax[0].plot([np.mean(_v[1]) for _v in deriv_orders.values()], label='Reference method', marker='o')
        # median
        ax[0].set_title("Absolute step sizes.")
        ax[0].set_xticks(range(len(sizes_step)), share_number_test_images)
        ax[0].set_ylabel('Deviation \n [Number of frames]')
        ax[0].legend()

        ax[1].plot([np.mean(_v[0]) / dl for _v, dl in zip(deriv_orders.values(), dataset_lengths)], label='TN method',
                   marker='o')
        ax[1].plot([np.mean(_v[1]) / dl for _v, dl in zip(deriv_orders.values(), dataset_lengths)],
                   label='Reference method', marker='o')
        ax[1].set_title("Relative step sizes normalized by number of frames in dataset.")
        ax[1].set_xlabel("Percentage of frames of original experiment in test dataset [%]")
        ax[1].set_ylabel('Step sizes \n [Number of frames]')

        plt.suptitle('Average step sizes of predicted image temporal ordering')
        plt.tight_layout()
        if kwargs.get('savefig', False):
            plt.savefig(kwargs.get('savefig'))
        else:
            plt.show()
        plt.close()


class FindTemporalSequenceTN:
    """
    This class serves as juncture between the above classes.
    It combines different nodes of the analysis pipeline
    for evaluation of a predicted image order using
    the Twin Network.
    """
    def __init__(self, resnet50):
        self.tool_inference = DataInferenceTemporalSequenceTN()
        self.tool_order = None
        self.values_ordered = None
        self.resnet50 = resnet50

    def __call__(self, dir_src):
        """
        Order images within a directory based on similarity values.
        """
        paths_imgs_src = self.step1_images_load(dir_src)
        embeddings_src, indices_imgs_src_shuffled = self.step2_embeddings_calculate(paths_imgs_src)
        indices_decoded = self.step3_embeddings_order(embeddings_src, indices_imgs_src_shuffled)
        return indices_decoded

    @staticmethod
    def step1_images_load(dir_src):
        """
        Load image paths from directory.
        """
        # 1. Dir src -> load image src paths
        paths_imgs_src = glob.glob(f'{dir_src}/*.tif')  # Order 1 (original)

        # 2. Image paths -> indexing
        paths_imgs_src = list(enumerate(sorted(paths_imgs_src)))  # Order 1 (original)

        # 3. Tuples (original indices, image paths) -> shuffle
        random.seed(1)
        random.shuffle(paths_imgs_src)  # Order 2 (Shuffled)
        return paths_imgs_src

    def step2_embeddings_calculate(self, paths_imgs_src):
        """
        Load images and calculate embeddings.
        """
        # 4. Shuffled tuples (original indices, image paths) -> split into shuffled indices, shuffled paths
        indices_imgs_src_shuffled = [index for index, _ in paths_imgs_src]  # Order 2 (shuffled) indices of paths
        paths_imgs_src_shuffled = [img for _, img in paths_imgs_src]  # Order 2 (shuffled)

        # 5. Shuffled tuples (original indices, image paths) -> embeddings
        embeddings_src = self.tool_inference.list_to_embeddings(paths_imgs_src_shuffled,
                                                                self.resnet50)  # Order 2 (shuffled)
        return embeddings_src, indices_imgs_src_shuffled

    def step3_embeddings_order(self, embeddings_src, indices_imgs_src_shuffled):
        """
        Order embeddings based on similarities and create a list
        of the indices of the embeddings in the predicted order.
        Use this list of the embedding indices to access original
        indices.
        Return a list with the indices of the input paths in the
        predicted order.
        """
        # 6. Shuffled image paths -> encode order in list of indices
        # of original shuffled indices that are supposedly in order
        self.tool_order = OrderTemporalSequenceTN(embeddings_src)
        values_ordered = self.tool_order()  # Order 3 indices of Order 2 indices

        idxs_ordered = [values_ordered[i]['idx_ordered'] for i in values_ordered.keys()]
        sums_zscores = [values_ordered[i]['sum_zscores'] for i in values_ordered.keys()]
        nums_nonmax = [values_ordered[i]['num_nonmax'] for i in values_ordered.keys()]

        print(f'Starting at index {np.argmax(sums_zscores)} led to highest sum of z-scores.')
        print(f'Starting at index {np.argmin(nums_nonmax)} led to lowest number of non-maximum similarity assignments.')
        start_index_nonmax_based = int(np.argmin(nums_nonmax))

        self.values_ordered = values_ordered[start_index_nonmax_based]
        # 7. Encoded ordered indices of indices -> decoded indices of paths
        indices_decoded = [indices_imgs_src_shuffled[i] for i in idxs_ordered[start_index_nonmax_based]]

        return indices_decoded
