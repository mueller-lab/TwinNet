import itertools
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

plt.rcParams['svg.fonttype'] = 'none'


class TNToolsPlotCompare:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used to plot embedding similarities
    between embeddings of two batches of objects.
    """
    def __init__(self):
        self.plot_cmap = matplotlib.cm.get_cmap("viridis")
        self.plot_figsize = (5, 3)
        self.plot_fontsize_large = 8
        self.plot_fontsize_small = 6
        self.plot_linewidth = 1
        self.plot_line_alpha_fg = 1
        self.plot_size_marker = self.plot_linewidth * 5

    @staticmethod
    def fn_set_box_params(bp, color, linewidth):
        """
        Update all boxplot parts with same color and linewidth.
        """
        plt.setp(bp['boxes'], color=color, linewidth=linewidth)
        plt.setp(bp['whiskers'], color=color, linewidth=linewidth)
        plt.setp(bp['caps'], color=color, linewidth=linewidth)
        plt.setp(bp['medians'], color=color, linewidth=linewidth)
        plt.setp(bp['fliers'], linestyle='none', markerfacecolor=color,
                 markersize=linewidth)

    @staticmethod
    def fn_calc_significance(atp_embryo_sims_a, atp_embryo_sims_b):
        """
        Calculate statistical significance between two arrays.
        First, use Shapiro-Wilk test to check if array values are
        normal-distributed. If both values are normal-distributed,
        calculate t-test for independent samples. If either
        one or both arrays are not normal-distributed,
        calculate Mann-Whitney-U-test.

        Parameters
        ----------
        atp_embryo_sims_a
        atp_embryo_sims_b
        """
        atp_embryo_sims_a = np.array(atp_embryo_sims_a)
        atp_embryo_sims_b = np.array(atp_embryo_sims_b)
        alpha_distribution = 5e-2
        distribution_normal = False
        try:
            _, p_a = stats.shapiro(atp_embryo_sims_a)
            _, p_b = stats.shapiro(atp_embryo_sims_b)
            if p_a >= alpha_distribution or p_b >= alpha_distribution:
                distribution_normal = True
        except:
            distribution_normal = True
        if distribution_normal:
            res = stats.ttest_ind(atp_embryo_sims_a, atp_embryo_sims_b)
        else:
            res = stats.mannwhitneyu(atp_embryo_sims_a, atp_embryo_sims_b)

        return res.pvalue

    def fn_calc_significance_embryos(self,
                                     atp_dataset_sims_positions_x,
                                     **kwargs):
        """
        Calculate statistical significance between multiple arrays
        of embryo similarity values. If a combination of arrays
        has significant difference of central tendency, return
        x-positions of plots for line plotting.

        Parameters
        ----------
        atp_dataset_sims_positions_x: dict
            Keys: acquisition timepoints
            Values: [
                {Key: dataset_name/str, value: similarities/list},
                {Key: dataset_name/str, value: x position of boxplot/float}
            ]

        Returns
        -------
        atp_positions_x_significance: dict
            Keys: acquisition timepoints
            Values: [
                list of [x_a, x_b, x_label, label, width]
                for significant combinations,
                position_y_max: numpy.float32 with maximum y value
                of similarities,
                position_y_min: numpy.float32 with minimum y value
                of similarities
            ]
        """
        atp_positions_x_significance = dict()
        positions_y_max = list()
        positions_y_min = list()

        for _tp, [atp_embryo_sims,
                  positions_x] in atp_dataset_sims_positions_x.items():
            if kwargs.get("verbose", False):
                print(f"Number of arrays: {len(atp_embryo_sims)}")

            # Combinations of (dataset_name, similarity values)
            combinations = itertools.combinations(
                list(atp_embryo_sims.items()), 2)

            positions_x_significance = list()

            # Loop through combinations
            for (_k_a, _v_a), (_k_b, _v_b) in combinations:
                # Calculate significance
                comb_pvalue = self.fn_calc_significance(_v_a, _v_b)
                x_a = positions_x[_k_a]
                x_b = positions_x[_k_b]

                # If p-value is below alpha for combination
                # return x-positions of plots for line plotting
                # and label of significance level

                if comb_pvalue < 0.05:
                    label_significance = "*"
                    if comb_pvalue < 0.01:
                        label_significance = "**"
                    if comb_pvalue < 0.001:
                        label_significance = "***"
                    # Structure: [x_a, x_b, x_label=
                    # center point between x_a and x_b,
                    # label_significance, distance between
                    # x_a and x_b]
                    positions_x_significance.append([
                        x_a, x_b, x_a + (x_b - x_a) / 2,
                        label_significance, x_a - x_b])

                positions_y_max.append(np.max([np.max(_v_a), np.max(_v_b)]))
                positions_y_min.append(np.min([np.max(_v_a), np.min(_v_b)]))

                # Structure: [list_x_positions_1, ...,
                # list_x_positions_n, maximum y value of boxplot]

            atp_positions_x_significance[_tp] = positions_x_significance

        position_y_max = np.max(positions_y_max) \
            if len(positions_y_max) != 0 else np.nan
        position_y_min = np.min(positions_y_min) \
            if len(positions_y_min) != 0 else np.nan

        return atp_positions_x_significance, position_y_max, position_y_min

    def fn_calc_significance_embryos_get_datasets(self,
                                                  atp_dataset_sims_positions_x,
                                                  **kwargs):
        """
        Similar function to 'fn_calc_significance_embryos'. This function
        is a lighter version, returning less information about
        x and y positions, but instead about dataset classes.

        Calculate statistical significance between multiple arrays
        of embryo similarity values. If a combination of arrays
        has significant difference of central tendency, return
        x-positions of plots for line plotting.

        Parameters
        ----------
        atp_dataset_sims_positions_x: dict
            Keys: acquisition timepoints
            Values: [
                {dataset_name (str): similarities/list},
                {dataset_name (str): x position of boxplot/float}
            ]

        Returns
        -------
        atp_positions_x_significance: dict
            Keys: acquisition timepoints
            Values: [
                list of [x, dataset_name, dataset_name]
                for significant combinations
            ]
        """
        atp_positions_x_significance = dict()

        # for tp, [dict with dataset names:
        # list of embryo similarities at tp, _]:
        for _tp, [atp_embryo_sims, _] in atp_dataset_sims_positions_x.items():
            if kwargs.get("verbose", False):
                print(f"Number of arrays: {len(atp_embryo_sims)}")

            # Combinations of (dataset_name, similarity values)
            combinations = itertools.combinations(
                list(atp_embryo_sims.items()), 2)

            positions_x_significance = list()

            # Loop through combinations
            for (_k_a, _v_a), (_k_b, _v_b) in combinations:
                # Calculate significance
                comb_pvalue = self.fn_calc_significance(_v_a, _v_b)

                if comb_pvalue < 0.05:
                    pass
                    if comb_pvalue < 0.01:
                        pass
                    if comb_pvalue < 0.001:
                        pass
                    # Structure: [k_a, dataset_name_a,
                    # dataset_name_b]
                    positions_x_significance.append([_k_a, _k_b])

            atp_positions_x_significance[_tp] = positions_x_significance

        return atp_positions_x_significance

    def fn_plot_ax_sims_mean_std_multiple(self,
                                          ax,
                                          mean_sims_plot,
                                          std_sims_plot,
                                          plot_xs,
                                          plot_color,
                                          plot_alpha_bg):
        """
        Plot the mean and standard deviation of similarities
        of embryos compared to embryos of other datasets
        onto a matplotlib.axes._subplots.AxesSubplot object.

        Parameters
        ----------
        ax: matplotlib.axes._subplots.AxesSubplot
        mean_sims_plot: list
        std_sims_plot: list
        plot_xs: list
        plot_color: tuple or str
        plot_alpha_bg: float

        Returns
        -------
        ax: matplotlib.axes._subplots.AxesSubplot
            Axis on which graphs were plotted.
        """
        values_err_low = np.array(mean_sims_plot) - np.array(std_sims_plot)
        values_err_high = np.array(mean_sims_plot) + np.array(std_sims_plot)

        sc = ax.scatter(plot_xs, mean_sims_plot,
                        color=plot_color,
                        linewidth=0,
                        marker='o',
                        s=self.plot_linewidth)
        bg = ax.fill_between(plot_xs, values_err_low, values_err_high,
                             alpha=plot_alpha_bg,
                             color=plot_color,
                             linewidth=0)

        return ax, (sc, bg)

    @staticmethod
    def fn_positions_x_significance_y_adjust(atp_positions_x_significance,
                                             position_y_max,
                                             position_y_min):
        """
        The method 'fn_calc_significance_embryos' returns a list
        of multiple lists with x-positions. This function checks how
        many line plots need to be plotted and adjusts the y-values
        for the lines accordingly.

        Parameters
        ----------
        atp_positions_x_significance: dict
            Keys: acquisition timepoints
            Values: list of [x_a, x_b, x_label, label, width]
                    for significant combinations
        position_y_max: numpy.float32 with maximum y value of similarities,
        position_y_min: numpy.float32 with minimum y value of similarities

        Returns
        -------
        atp_positions_x_y_lines: dict
        atp_positions_x_y_text: dict
        """
        atp_positions_x_y_lines = dict()
        atp_positions_x_y_text = dict()

        positions_y_range = position_y_max - position_y_min
        plot_height_bar_significance = positions_y_range * 0.02
        plot_step_y_bar_significance = positions_y_range * 0.04
        plot_step_text_significance = positions_y_range * 0.01
        plot_text_fontsize = 20
        for _tp, positions_x_significance in atp_positions_x_significance \
                .items():

            if position_y_max != np.nan:
                # Sort by longest distance between x_a and x_b
                positions_x_significance.sort(key=lambda x: x[-1])

                positions_x_y_lines = list()
                positions_x_y_text = list()

                for i in range(len(positions_x_significance)):
                    [x_a, x_b, x_label, label, _] = positions_x_significance[i]
                    y = position_y_max + plot_step_y_bar_significance * (i + 1)
                    xs_ys = [[x_a, x_b],
                             [y, y + plot_height_bar_significance]]
                    positions_x_y_lines.append(xs_ys)
                    positions_x_y_text.append([x_label,
                                               y + plot_step_text_significance,
                                               label,
                                               plot_text_fontsize])

                atp_positions_x_y_lines[_tp] = positions_x_y_lines
                atp_positions_x_y_text[_tp] = positions_x_y_text

        return atp_positions_x_y_lines, atp_positions_x_y_text

    def plot_similarities_mean_std_multiple(self,
                                            list_mean_sims_plot,
                                            list_std_sims_plot,
                                            list_names,
                                            list_datasets_colors,
                                            **kwargs):
        """
        Plot the mean and standard deviation of similarities
        of embryos compared to embryos of other datasets
        as line plot with an error bound for multiple
        sets of comparisons.

        Parameters
        ----------
        list_mean_sims_plot: list of lists
        list_std_sims_plot: list of lists
        list_names: list of strs
        list_datasets_colors: list of tuples or strs
        """
        plot_atp_adjustment_timepoint = int(
            kwargs.get("adjustment_timepoints", 2)
        )

        num_timepoints_reference = 0
        for mean_sims_plot, std_sims_plot in zip(list_mean_sims_plot,
                                                 list_std_sims_plot):
            assert len(mean_sims_plot) == len(std_sims_plot), \
                "Mean and standard values not equally long."
            num_timepoints_reference = max(num_timepoints_reference,
                                           len(mean_sims_plot))

        plot_alpha_bg = 0.1
        plot_legend_handles = list()
        plot_xs = list(range(1, num_timepoints_reference + 1))
        plot_x_ticks = list(range(0, num_timepoints_reference, 50))
        plot_ymax = list()
        plot_ymin = list()
        fig, ax = plt.subplots(1,
                               dpi=300,
                               figsize=self.plot_figsize)

        for mean_sims_plot, std_sims_plot, name in zip(list_mean_sims_plot,
                                                       list_std_sims_plot,
                                                       list_names):
            plot_ymax.append(np.max(
                np.array(mean_sims_plot) + np.array(std_sims_plot)))
            plot_ymin.append(np.min(
                np.array(mean_sims_plot) - np.array(std_sims_plot)))
            ax, plot_handle = self.fn_plot_ax_sims_mean_std_multiple(
                ax,
                mean_sims_plot,
                std_sims_plot,
                plot_xs,
                list_datasets_colors[name],
                plot_alpha_bg)

            plot_legend_handles.append(plot_handle)

        plt.xlabel('Time (min)', fontsize=self.plot_fontsize_large)
        plt.xlim(0, num_timepoints_reference)
        plt.xticks(plot_x_ticks,
                   [str(x * plot_atp_adjustment_timepoint)
                    for x in plot_x_ticks],
                   fontsize=self.plot_fontsize_small)
        plt.ylabel('Cosine similarity φ', fontsize=self.plot_fontsize_large)
        plt.ylim(bottom=np.min(plot_ymin) * 0.9, top=1.0)
        plt.yticks(fontsize=self.plot_fontsize_small)
        plt.legend(plot_legend_handles, list_names,
                   fontsize=self.plot_fontsize_small, frameon=False)

        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'], dpi=300)
        plt.show()
        plt.close()

    def plot_similarities_mean_std_multiple_significance(
            self,
            list_datasets_plot,
            list_datasets_mean_sims_plot,
            list_datasets_std_sims_plot,
            list_datasets_names,
            list_datasets_colors,
            **kwargs):
        """
        Plot the mean and standard deviation of similarities
        of embryos compared to embryos of other datasets
        as line plot with an error bound for multiple
        sets of comparisons. Plot significances in
        difference of central tendency between datasets
        as dots.

        Parameters
        ----------
        list_datasets_plot: list of dicts
        list_datasets_mean_sims_plot: list of lists
        list_datasets_std_sims_plot: list of lists
        list_datasets_names: list of strs
        list_datasets_colors: list of tuples or strs
        kwargs: Variable keyword arguments
        """
        num_datasets = len(list_datasets_names)
        num_timepoints = list()

        # Plot mean and std first
        for mean_sims_plot, std_sims_plot in zip(
                list_datasets_mean_sims_plot,
                list_datasets_std_sims_plot):
            assert len(mean_sims_plot) == len(std_sims_plot), \
                "Mean and standard values not equally long."
            num_timepoints.append(len(mean_sims_plot))
        # Loop through datasets and embryo, get number of
        # similarity values per embryo and thus get number of
        # maximum timepoints per datasets
        tp_maxima = [np.max([len(embryo_sims)
                             for embryo_id, embryo_sims
                             in dataset_plot.items()])
                     for dataset_plot in list_datasets_plot]
        assert np.std(tp_maxima) == float(0), \
            "Number of similarity values differs between different lists."
        num_timepoints_reference = max(tp_maxima)

        plot_alpha_bg = 0.1
        plot_atp_min_correction = int(kwargs.get('adjustment_timepoints', 1))
        plot_legend_handles = list()
        plot_xs = list(range(1, num_timepoints_reference + 1))
        plot_x_ticks = list(range(0, num_timepoints_reference, 50))
        plot_y_pos_shift = 1
        plot_ymax = list()
        plot_ymin = list()

        fig, ax = plt.subplots(2, 1, dpi=300,
                               figsize=self.plot_figsize,
                               gridspec_kw={'height_ratios': [0.8, 0.2],
                                            'hspace': 0.0},
                               sharex=True)

        # Loop through datasets separately
        for mean_sims_plot, std_sims_plot, name in zip(
                list_datasets_mean_sims_plot,
                list_datasets_std_sims_plot,
                list_datasets_names):
            # Get maximum y value to plot for dataset
            plot_ymax.append(np.max(
                np.array(mean_sims_plot) + np.array(std_sims_plot)))
            # Get minimum y value to plot for dataset
            plot_ymin.append(np.min(
                np.array(mean_sims_plot) - np.array(std_sims_plot)))
            # Plot lines and standard deviation for
            # each dataset separately to ax[0]
            ax[0], plot_handle = self.fn_plot_ax_sims_mean_std_multiple(
                ax[0],
                mean_sims_plot,
                std_sims_plot,
                plot_xs,
                list_datasets_colors[name],
                plot_alpha_bg
            )
            # Add handles of plot to list for making
            # a legend later in code
            plot_legend_handles.append(plot_handle)

        # Plot significances in second axis
        # Get combinations for which significances
        # should be calculated
        combinations_datasets = list(
            itertools.combinations(list_datasets_names, 2)
        )
        num_combinations = len(combinations_datasets)

        # For each combination of datasets, assign
        # y-position where indicators of significances
        # should be plotted in second axis
        y_positions = {
            dataset_name: y_pos * plot_y_pos_shift
            for dataset_name, y_pos
            in zip(
                combinations_datasets,
                range(num_combinations)
            )
        }

        # Rearrange lists of similarity values: Instead of
        # dataset/embryo/list of similarity values
        # (timepoints implicit by image order) sort as
        # timepoint/dataset/embryo similarities
        # (embryo similarities not sorted by embryos anymore,
        # timepoints are sorted explicitly after iteration
        # through max number of timepoints)
        sims_resort_tp = {
            int(_tp): {
                dataset_name: [
                    embryo_sims[_tp]
                    for embryo_id, embryo_sims
                    in dataset_plot.items()]
                for dataset_plot, dataset_name
                in zip(
                    list_datasets_plot, list_datasets_names)
            }
            for _tp in range(tp_maxima[0])}

        # In the next step we want to reformat the data structure
        # once again. Change from:
        # timepoint/dataset/embryo
        # to
        # timepoint/
        #     [dict-> dataset name: embryo similarity values (list),
        #     dict -> dataset name: x-position (equalling timepoint; float)]
        atp_dataset_sims_positions_x = dict()

        for _tp, atp_dataset_sims in sims_resort_tp.items():
            # Dict to save positions of boxplots by name
            dataset_positions_x = dict()

            # Loop through datasets at respective acquisition timepoint
            for i in range(num_datasets):
                dataset_name = sorted(list(atp_dataset_sims.keys()))[i]

                # Calculate x position for boxplot and save in dictionary
                pos_x = float(_tp)
                dataset_positions_x[dataset_name] = pos_x

            # Assign similarity values and x_positions to
            # dictionary for significance calculation
            atp_dataset_sims_positions_x[_tp] = [atp_dataset_sims,
                                                 dataset_positions_x]

        # Use dictionary and calculate if distributions of similarities
        # contain significance at each acquisition timepoint
        atp_positions_x_significance = self. \
            fn_calc_significance_embryos_get_datasets(
                atp_dataset_sims_positions_x
            )
        # Hereby we get a dictionary, where keys are x-values
        # (i.e., acquisition timepoints) and values are two-item
        # lists of name combinations for those comparisons that
        # are significantly different, also stored as list

        # Loop through this dictionary and plot line for those
        # combinations that are significantly different

        # for atp, [list of possibly multiple two-item lists
        # with dataset names that show significant difference]:
        for atp, keys in atp_positions_x_significance.items():
            # Loop through the significant combinations, if any
            for i in range(len(keys)):
                [_k_a, _k_b] = keys[i]
                # Get y position of that combination of keys
                # (dataset names) that we prepared earlier
                y_pos = y_positions[(_k_a, _k_b)]
                ax[1].plot(
                    atp,
                    y_pos,
                    c=list_datasets_colors[_k_a],
                    marker=2,  # Marker is tick up
                    markersize=plot_y_pos_shift * 2
                )
                ax[1].plot(
                    atp,
                    y_pos,
                    c=list_datasets_colors[_k_b],
                    marker=3,  # Marker is tick down
                    markersize=plot_y_pos_shift * 2
                )

        # Adjust plot parameters
        ax[0].legend(plot_legend_handles,
                     list_datasets_names,
                     fontsize=self.plot_fontsize_small,
                     frameon=True)

        ax[0].tick_params(axis='both', which='both',
                          labelsize=self.plot_fontsize_small)
        ax[0].set_xlim(0, num_timepoints_reference)
        ax[0].set_xticks(plot_x_ticks,
                         [str(x * plot_atp_min_correction)
                          for x in plot_x_ticks],
                         fontsize=self.plot_fontsize_small)
        ax[0].set_ylabel('Cosine similarity φ',
                         fontsize=self.plot_fontsize_large)
        ax[0].set_ylim(bottom=np.min(plot_ymin), top=1.0)

        ax[1].tick_params(axis='both', which='both',
                          labelsize=self.plot_fontsize_small)
        # To plot ylim for ax[1], do following:
        # - Get median y value of plots
        # - Calculate distance of median value to lowest and highest y value
        ax[1].set_ylim(
            bottom=min(
                list(y_positions.values())) - plot_y_pos_shift,
            top=max(
                list(y_positions.values())) + plot_y_pos_shift)
        ax[1].set_yticks([])
        ax[1].set_xlabel("Time (min)",
                         fontsize=self.plot_fontsize_large)
        ax[1].set_ylabel("Significant\ndifference",
                         fontsize=self.plot_fontsize_large)

        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'], dpi=300)
        plt.show()
        plt.close()

    def plot_similarities_mean_std_multiple_zoom(self,
                                                 list_datasets_plot,
                                                 list_datasets_names,
                                                 list_datasets_colors,
                                                 bound_lower,
                                                 bound_upper,
                                                 **kwargs):
        """
        Plot the mean and standard deviation of similarities
        of embryos compared to embryos of other datasets.
        Plot sequence in a specified range as boxplots with
        an error bound for multiple sets of comparisons.

        Parameters
        ----------
        list_datasets_plot: list of lists
        list_datasets_names: list of strs
        list_datasets_colors: list of strs
        bound_lower: int or float
        bound_upper: int or float
        """
        # Get number of different datasets in list of similarities
        num_datasets = len(list_datasets_names)

        # Get maximum number of acquisition timepoints in list of similarities
        tp_maxima = [np.max(
            [len(embryo_sims)
             for embryo_id, embryo_sims in dataset_plot.items()])
            for dataset_plot in list_datasets_plot]

        # Prepare range based on acquisition timepoints for plotting
        tp_values_range = list(range(bound_lower, bound_upper + 1))

        # Assert that number of similarity values of datasets are equal
        assert np.std(tp_maxima) == float(0), \
            "Number of similarity values differs between different lists."

        # Plot parameters
        plot_adjustment_timepoints = int(kwargs.get("adjustment_timepoints",
                                                    2))
        plot_boxplot_shift_max = 0.2
        plot_boxplot_shift = plot_boxplot_shift_max * 2 / (num_datasets - 1)
        plot_boxplots_positions = list(
            np.arange(-plot_boxplot_shift_max,
                      plot_boxplot_shift_max + plot_boxplot_shift * 0.5,
                      plot_boxplot_shift))
        plot_legend_handles = dict()

        # Rearrange lists of similarity values:
        # Initial sorting:
        # [ {k = embryo ID,
        #    v = similarity values ordered by acquisition timepoints},
        #   ...
        # ]
        # Sort to:
        # {k = acquisition timepoint 1:
        #  v = {dataset_name 1: [similarity values at acquisition timepoint 1
        #                        of all embryos in dataset 1],
        #       ...
        #       dataset_name n: [similarity values at acquisition timepoint 1
        #                        of all embryos in dataset n]},
        #  ...,
        #  k = acquisition timepoint m}
        sims_resort_tp = {
            int(_tp): {
                dataset_name: [
                    embryo_sims[_tp]
                    for embryo_id, embryo_sims in dataset_plot.items()]
                for dataset_plot, dataset_name in zip(list_datasets_plot,
                                                      list_datasets_names)
            }
            for _tp in range(tp_maxima[0])
        }

        # Adjust interval to specified interval of interest
        sims_resort_tp_sliced = {
            _tp: atp_embryo_sims
            for _tp, atp_embryo_sims in sims_resort_tp.items()
            if int(_tp) in tp_values_range
        }

        # Minima and maxima for errorbound
        ymins_ymaxs_by_timepoints = {
            _tp: {dataset_name: {
                "min": np.min(atp_embryo_sims),
                "max": np.max(atp_embryo_sims)}
                for dataset_name, atp_embryo_sims in atp_dataset_sims.items()}
            for _tp, atp_dataset_sims in sims_resort_tp_sliced.items()
        }

        ymins_ymaxs_by_dataset_names = {
            dataset_name: [[
                atp_dataset_ymin_ymax[dataset_name]["min"],
                atp_dataset_ymin_ymax[dataset_name]["max"]
            ]
                for _tp, atp_dataset_ymin_ymax
                in ymins_ymaxs_by_timepoints.items()
            ]
            for dataset_name in ymins_ymaxs_by_timepoints[bound_lower].keys()
        }

        # Minima for plot frame
        ymins = [np.min([np.min(atp_embryo_sims)
                         for atp_embryo_sims in atp_dataset_sims.values()])
                 for _tp, atp_dataset_sims in sims_resort_tp_sliced.items()]

        # Plot figure
        fig, ax = plt.subplots(1, dpi=300,
                               figsize=self.plot_figsize
                               # figsize=(len(tp_values_range) * 2,
                               #          len(tp_values_range) * 0.8)
                               )

        # Boxplots
        atp_dataset_sims_positions_x = dict()

        # Loop through acquisition timepoints
        for _tp, atp_dataset_sims in sims_resort_tp_sliced.items():
            # Dict to save positions of boxplots by name
            dataset_positions_x = dict()

            # Loop through datasets at respective acquisition timepoint
            for i in range(num_datasets):
                # Get dataset name
                dataset_name = sorted(list(atp_dataset_sims.keys()))[i]
                atp_embryo_sims = atp_dataset_sims[dataset_name]

                # Save boxplot position in dictionary
                pos_x = float(_tp + plot_boxplots_positions[i])
                dataset_positions_x[dataset_name] = pos_x

                # Plot boxplot and adjust parameters
                boxp = ax.boxplot(atp_embryo_sims, positions=[pos_x])
                self.fn_set_box_params(boxp,
                                       list_datasets_colors[dataset_name],
                                       self.plot_linewidth)

            # Assign similarity values and x_positions to
            # dictionary for significance calculation
            atp_dataset_sims_positions_x[_tp] = [atp_dataset_sims,
                                                 dataset_positions_x]

        # Use dictionary and calculate if distributions of similarities
        # are significantly different at each acquisition timepoint
        atp_positions_x_significance, \
        position_y_max, \
        position_y_min = self.fn_calc_significance_embryos(
            atp_dataset_sims_positions_x)

        # Convert calculated significances to lines and text for plotting
        atp_positions_x_y_lines, \
        atp_positions_x_y_text = self.fn_positions_x_significance_y_adjust(
            atp_positions_x_significance,
            position_y_max,
            position_y_min)

        # If there are significant combinations of arrays, plot as lines
        # for _tp, positions_x_y_lines in atp_positions_x_y_lines.items():
        #     if len(positions_x_y_lines) != 0:
        #         for [[x1, x2], [y1, y2]] in positions_x_y_lines:
        #             ax.plot([x1, x1, x2, x2], [y1, y2, y2, y1],
        #                     color=plot_significance_color,
        #                     linewidth=plot_linewidth_significance)

        # If there are significant combinations of arrays plot as text
        for _tp, positions_x_y_text in atp_positions_x_y_text.items():
            if len(positions_x_y_text) != 0:
                for [x_label, y_label, label, fontsize] in positions_x_y_text:
                    ax.text(x_label, y_label, label,
                            color='k',
                            fontsize=self.plot_fontsize_small,
                            ha="center",
                            va="bottom")

        # Adjust plot parameters
        plt.tick_params(axis='both', which='both',
                        labelsize=self.plot_fontsize_small)
        plt.xlabel('Time (min)', fontsize=self.plot_fontsize_large)
        if len(tp_values_range) > 20:
            plt.xticks(tp_values_range[::5],
                       [tp * plot_adjustment_timepoints
                        for tp in tp_values_range[::5]],
                       fontsize=self.plot_fontsize_small)
        else:
            plt.xticks(tp_values_range,
                       [tp * plot_adjustment_timepoints
                        for tp in tp_values_range],
                       fontsize=self.plot_fontsize_small)
        plt.ylabel('Cosine similarity φ',
                   fontsize=self.plot_fontsize_large)
        plt.ylim(bottom=np.min(ymins) * 0.995, top=1.0)
        plt.yticks(fontsize=self.plot_fontsize_small)
        if kwargs.get("plot_legend", False):
            plt.legend(list(plot_legend_handles.values()),
                       list(plot_legend_handles.keys()),
                       fontsize=self.plot_fontsize_small,
                       frameon=True)

        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'], dpi=300)
        plt.show()
        plt.close()

    def plot_similarity_trajectories(self, list_datasets_sims, **kwargs):
        """
        Create a graph displaying similarities of embryos
        compared to embryos of other datasets.
        """
        plot_atp_adjustment_timepoint = int(
            kwargs.get("adjustment_timepoints", 2)
        )
        num_timepoints_reference = np.max(
            [len(_v) for _v in list_datasets_sims.values()]
        )
        plot_xs = list(range(1, num_timepoints_reference + 1))
        plot_x_ticks = list(range(0, num_timepoints_reference, 100))

        fig, ax = plt.subplots(1, dpi=300, figsize=self.plot_figsize)

        # Enumerate keys of embryos
        _ks_embryos_enumerate = list(enumerate(sorted(list_datasets_sims.keys())))
        # Get maximum number of enumeration of embryo keys, to scale
        # assigned numbers between 0 - 1. Convert to dictionary with
        # keys: embryo keys, values: embryo numbers/highest embryo number
        _ks_embryos_enumerate_max = max(_ks_embryos_enumerate,
                                        key=lambda item: item[0])
        # Max returns tuple
        _ks_embryos_cmap = {
            _v[1]: _v[0] / _ks_embryos_enumerate_max[0]
            for _v in _ks_embryos_enumerate
        }

        for _k_embryo, _v_embryo in sorted(list_datasets_sims.items()):
            plt.plot(plot_xs,
                     _v_embryo,
                     color=self.plot_cmap(_ks_embryos_cmap[_k_embryo]),
                     label=_k_embryo,
                     linewidth=self.plot_linewidth)

        ax.tick_params(axis='both',
                       which='both',
                       labelsize=self.plot_fontsize_small)
        ax.set_xlabel('Time (min)', fontsize=self.plot_fontsize_large)
        ax.set_xlim(0, num_timepoints_reference)
        ax.set_xticks(plot_x_ticks,
                      [str(x * plot_atp_adjustment_timepoint)
                       for x in plot_x_ticks],
                      fontsize=self.plot_fontsize_small)
        ax.set_ylabel('Cosine similarity φ',
                      fontsize=self.plot_fontsize_large)
        ax.set_ylim(bottom=0.0, top=1.0)
        if kwargs.get("title", None) is not None:
            ax.set_title(kwargs["title"],
                         fontsize=self.plot_fontsize_large)
        plt.legend(fontsize=self.plot_fontsize_small, loc=3)

        if kwargs.get("path_save", None) is not None:
            plt.savefig(kwargs['path_save'], dpi=300)
        plt.show()
        plt.close()

    def plot_similarity_trajectories_with_errorbound(self,
                                                     plot_means,
                                                     plot_std,
                                                     plot_color,
                                                     **kwargs):
        """
        Create a graph displaying the average of similarities
        of embryos compared to embryos of other datasets,
        as line plot with an error bound.
        """
        assert len(plot_means) == len(plot_std), \
            "Mean and standard values not equally long."

        plot_atp_adjustment_timepoint = int(
            kwargs.get("adjustment_timepoints", 2)
        )
        num_timepoints_reference = len(plot_means)
        values_err_low = np.array(plot_means) - np.array(plot_std)
        values_err_high = np.array(plot_means) + np.array(plot_std)

        plot_xs = list(range(1, num_timepoints_reference + 1))
        plot_x_ticks = list(range(0, num_timepoints_reference, 100))

        fig, ax = plt.subplots(1, dpi=300, figsize=self.plot_figsize)

        ax.plot(plot_xs, plot_means,
                label='Mean',
                color=plot_color,
                linewidth=self.plot_linewidth)
        plt.fill_between(plot_xs, values_err_low, values_err_high,
                         alpha=0.1,
                         color=plot_color,
                         label='Standard deviation')

        ax.tick_params(axis='both',
                       which='both',
                       labelsize=self.plot_fontsize_small)
        ax.set_xlabel('Time (min)', fontsize=self.plot_fontsize_large)
        ax.set_xlim(0, num_timepoints_reference)
        ax.set_xticks(plot_x_ticks,
                      [str(x * plot_atp_adjustment_timepoint)
                       for x in plot_x_ticks],
                      fontsize=self.plot_fontsize_small)
        ax.set_ylabel('Cosine similarity φ',
                      fontsize=self.plot_fontsize_large)
        ax.set_ylim(bottom=0.0, top=1.0)
        if kwargs.get("title", None) is not None:
            ax.set_title(kwargs["title"],
                         fontsize=self.plot_fontsize_large)

        if kwargs.get("path_save", None) is not None:
            plt.savefig(kwargs['path_save'], dpi=300)
        plt.show()
        plt.close()

    def plot_similarity_trajectories_with_errorbound_for_movie(self,
                                                               plot_means,
                                                               plot_std,
                                                               plot_color,
                                                               path_img_test,
                                                               path_img_ref,
                                                               timepoint,
                                                               **kwargs):
        """
        Create a graph displaying the average of similarities
        of embryos compared to embryos of other datasets,
        as line plot with an error bound.

        Similar to previous method
        'plot_similarity_trajectories_with_errorbound', but returns
        figure axis instead of showing figure.
        """
        assert len(plot_means) == len(plot_std), \
            "Mean and standard values not equally long."

        plot_atp_adjustment_timepoint = int(
            kwargs.get("adjustment_timepoints", 2)
        )
        num_timepoints_reference = len(plot_means)
        values_err_low = np.array(plot_means) - np.array(plot_std)
        values_err_high = np.array(plot_means) + np.array(plot_std)

        plot_labelpad = 2
        plot_xs = list(range(1, num_timepoints_reference + 1))
        plot_x_ticks = list(range(0, num_timepoints_reference, 100))

        fig = plt.figure(dpi=300,
                         figsize=(5, 5))
        gs = fig.add_gridspec(2, 2)
        ax_plot = fig.add_subplot(gs[0, :])
        ax_img_test = fig.add_subplot(gs[1, 0])
        ax_img_ref = fig.add_subplot(gs[1, 1])

        ax_plot.plot(plot_xs, plot_means,
                     label='Mean',
                     color=plot_color,
                     linewidth=self.plot_linewidth)
        ax_plot.fill_between(plot_xs, values_err_low, values_err_high,
                             alpha=0.1,
                             color=plot_color,
                             label='Standard deviation')
        ax_plot.plot([timepoint, timepoint], [0, 1], 'r-', lw=1)

        ax_plot.tick_params(axis='both',
                            which='both',
                            labelsize=self.plot_fontsize_small)
        ax_plot.set_xlabel('Time (min)',
                           fontsize=self.plot_fontsize_large,
                           labelpad=plot_labelpad)
        ax_plot.set_xlim(0, num_timepoints_reference)
        ax_plot.set_xticks(plot_x_ticks,
                           [str(x * plot_atp_adjustment_timepoint)
                            for x in plot_x_ticks],
                           fontsize=self.plot_fontsize_small)
        ax_plot.set_ylabel('Cosine similarity φ',
                           fontsize=self.plot_fontsize_large)
        ax_plot.set_ylim(bottom=0.0, top=1.0)

        ax_img_ref.imshow(plt.imread(path_img_ref),
                          aspect="auto",
                          cmap='gray')

        ax_img_test.imshow(plt.imread(path_img_test),
                           aspect="auto",
                           cmap='gray')

        for ax in [ax_img_test, ax_img_ref]:
            ax.axis('off')

        return fig
