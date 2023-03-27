import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .tninference import TNToolsSimilarities


class TNToolsPlot:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used to plot embedding similarities.
    """

    def __init__(self):
        self.plot_line_alpha_fg = 1
        self.plot_line_colors = ["#fde725",
                                 "#35b779",
                                 "#31688e",
                                 "#1f4696",
                                 "#ed1c24"]
        self.plot_line_colors_difference = ["#25858e",
                                            "#482173"]
        self.plot_line_width = 1

        self.plot_fig_dpi = 300
        self.plot_fig_size = (5, 3)
        self.plot_fig_size_square = (4, 4)

        self.plot_fontsize_large = 8
        self.plot_fontsize_small = 6

        self.plot_marker_size = self.plot_line_width * 5
        self.plot_marker_size_mean = self.plot_line_width * 8

        self.plot_text_weight = 'ultralight'

        self.tools_similarities = TNToolsSimilarities()

    def plot_similarity_curve(self, path_df, path_save=None, **kwargs):
        """
        Plot mean of calculated similarities of images
        from dataframe.
        """
        # Dataframe
        if isinstance(path_df, str):
            path_df = pd.read_csv(path_df)
        df = path_df
        df_mean = df.mean(axis=1)
        df_similarity_high = df.loc[df['Anch_sim_1'] > 0.8]
        num_timepoints_reference = len(df)

        # Plot parameters
        plot_atp_min_correction = int(kwargs.get('intervals', 4))
        plot_label_x = f'Time (min)'
        plot_label_y = "Cosine similarity φ"
        plot_xs = range(1, num_timepoints_reference + 1)
        plot_x_ticks = list(range(0, num_timepoints_reference, 50))

        # Figure
        fig, (ax_hist, ax_box) = plt.subplots(
            2,
            dpi=self.plot_fig_dpi,
            figsize=self.plot_fig_size,
            gridspec_kw={"height_ratios": (.85, .15)},
            sharex=True
        )

        # Plot similarities
        ax_hist.scatter(plot_xs,
                        df_mean,
                        alpha=self.plot_line_alpha_fg,
                        c=self.plot_line_colors[2],
                        label='Mean',
                        marker='o',
                        linewidth=0,
                        s=self.plot_marker_size)

        ax_hist.set_xlim(left=0,
                         right=num_timepoints_reference)
        ax_hist.set_ylabel(plot_label_y,
                           fontsize=self.plot_fontsize_large,
                           weight=self.plot_text_weight)
        ax_hist.set_ylim(0, 1)
        ax_hist.tick_params(axis='both',
                            labelsize=self.plot_fontsize_small)
        ax_hist.set_xticks(plot_x_ticks,
                           [str(x * plot_atp_min_correction)
                            for x in plot_x_ticks],
                           fontsize=self.plot_fontsize_small)

        ax_hist.tick_params(axis='x',
                            which='both',
                            bottom=False,
                            top=False,
                            labelbottom=False)
        plt.setp(ax_hist.get_xticklabels(), visible=False)

        # Plot boxplot
        ax_box.scatter(df_similarity_high['Anch_sim_1'].idxmax(),
                       [0],  # y-value for plot in boxplot axis
                       c='r',
                       s=self.plot_marker_size_mean)
        ax_box.set_xlabel(plot_label_x,
                          fontsize=self.plot_fontsize_large,
                          weight=self.plot_text_weight)
        boxplot = ax_box.boxplot(
            x=df_similarity_high.index.values,
            boxprops={'facecolor': self.plot_line_colors[2],
                      'linewidth': self.plot_line_width},
            capprops={'linewidth': self.plot_line_width},
            flierprops={'marker': '.',
                        'markersize': self.plot_marker_size},
            medianprops={'color': (0, 0, 0),
                         'linewidth': self.plot_line_width},
            patch_artist=True,
            positions=[0],
            vert=False,
            widths=0.5,
            whiskerprops={'linewidth': self.plot_line_width},
            zorder=0)
        ax_box.tick_params(axis='both', labelsize=self.plot_fontsize_small)
        ax_box.set_yticks([])
        ax_box.linewidth = 0.1

        # Quartile highlight
        q25_mean = boxplot["whiskers"][0].get_path().get_extents().x1
        median_mean = boxplot["medians"][0].get_path().get_extents().x1
        q75_mean = boxplot["whiskers"][1].get_path().get_extents().x0

        ax_hist.add_patch(
            patches.Rectangle((q25_mean, 0),
                              q75_mean - q25_mean,
                              1,
                              facecolor=self.plot_line_colors[2],
                              alpha=0.1))
        ax_hist.plot([median_mean, median_mean],
                     [0, 1],
                     color=self.plot_line_colors[2],
                     linewidth=self.plot_line_width,
                     alpha=0.4)

        ax_box.add_patch(
            patches.Rectangle((q25_mean, -0.5),
                              q75_mean - q25_mean,
                              1,
                              facecolor=self.plot_line_colors[2],
                              alpha=0.1))
        ax_box.plot([median_mean, median_mean],
                    [-0.5, 0.5],
                    color=self.plot_line_colors[2],
                    linewidth=self.plot_line_width,
                    alpha=0.4)

        # Formatting
        plt.subplots_adjust(hspace=0)

        if path_save is not None:
            plt.savefig(path_save, dpi=fig.dpi)
        plt.show()
        plt.close(fig)

    def plot_similarity_maxima(self, df_sims, **kwargs):
        """
        Plot maxima of similarity sequence.

        Parameters
        ----------
        df_sims: pandas.core.frame.DataFrame
        **kwargs: See below

        Keyword Arguments
        ------------------------
        intervals_x: int
        Time intervals (min), at which reference embryos
            were acquired. Default is 4 minutes.
        intervals_y: int
            Time intervals (min), at which reference embryos
            were acquired. Default, corresponding to default
            set of reference embryos, is 4 minutes.
        """

        num_timepoints_query = df_sims.shape[0]
        num_timepoints_reference = df_sims.shape[1]

        plot_atp_min_correction_x = int(kwargs.get('intervals_x', 4))
        plot_atp_min_correction_y = int(kwargs.get('intervals_y', 4))
        plot_axis = 1
        plot_label_x = "Query embryo time (min)"
        plot_label_y = "Reference embryo time (min)"

        # Make axes equal length
        # Calculate durations of data sets
        duration_query = num_timepoints_query *\
                         plot_atp_min_correction_x
        duration_reference = num_timepoints_reference *\
                             plot_atp_min_correction_y
        # Get longer duration
        plot_range = max(duration_query, duration_reference)

        # Make tick labels based on timepoints
        plot_tick_labels = [int(i) for i in list(range(0, plot_range, 200))]

        # Divide timepoints by acquisition time intervals
        # to get indices for plotting
        plot_xs = range(1, num_timepoints_query + 1)
        plot_x_ticks = [plot_tick_label / plot_atp_min_correction_x
                        for plot_tick_label in plot_tick_labels]
        plot_y_ticks = [plot_tick_label / plot_atp_min_correction_y
                        for plot_tick_label in plot_tick_labels]

        plot_maxima = df_sims.idxmax(axis=plot_axis)
        plot_true_values = kwargs.get("true_values", [])

        # Plot
        fig, axs = plt.subplots(dpi=self.plot_fig_dpi,
                                figsize=self.plot_fig_size_square)

        axs.scatter(plot_xs,
                    plot_maxima,
                    alpha=self.plot_line_alpha_fg,
                    c=self.plot_line_colors[3],
                    label='Mean',
                    marker='o',
                    linewidth=0,
                    s=self.plot_marker_size)
        axs.plot(plot_true_values,
                 c=self.plot_line_colors[4],
                 label='Theoretical true value',
                 lw=self.plot_line_width)

        axs.set_xlabel(plot_label_x,
                       fontsize=self.plot_fontsize_large)
        axs.set_xlim(0, int(plot_range / plot_atp_min_correction_x))
        axs.set_xticks(plot_x_ticks,
                       plot_tick_labels,
                       fontsize=self.plot_fontsize_small)

        axs.set_ylabel(plot_label_y,
                       fontsize=self.plot_fontsize_large)
        axs.set_ylim(0, int(plot_range / plot_atp_min_correction_y))
        axs.set_yticks(plot_y_ticks,
                       plot_tick_labels,
                       fontsize=self.plot_fontsize_small)

        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'], dpi=self.plot_fig_dpi)
        plt.show()
        plt.close(fig)

    def plot_similarity_differences(self, df_earlier, df_later, **kwargs):
        """
        Plot differences in calculated similarities
        of two subsequently acquired images.
        """
        # Calculate similarity differences
        df_earlier_mean, df_later_mean, df_diff = \
            self.tools_similarities.fn_calculate_similarity_differences(
                df_earlier, df_later
            )

        num_timepoints_reference = len(df_earlier_mean)
        plot_atp_min_correction = int(kwargs.get('intervals', 4))
        plot_xs = list(range(1, num_timepoints_reference + 1))
        plot_x_ticks = list(range(0, num_timepoints_reference, 50))

        fig, ax_hist = plt.subplots(1,
                                    dpi=self.plot_fig_dpi,
                                    figsize=self.plot_fig_size)

        ax_hist.scatter(plot_xs,
                        df_earlier_mean,
                        alpha=self.plot_line_alpha_fg,
                        c=self.plot_line_colors_difference[0],
                        label='Earlier',
                        marker='o',
                        linewidth=0,
                        s=self.plot_marker_size)
        ax_hist.scatter(plot_xs,
                        df_later_mean,
                        alpha=self.plot_line_alpha_fg,
                        c=self.plot_line_colors_difference[1],
                        label='Later',
                        marker='o',
                        linewidth=0,
                        s=self.plot_marker_size)
        ax_hist.scatter(plot_xs,
                        df_diff,
                        alpha=self.plot_line_alpha_fg,
                        c=self.plot_line_colors[3],
                        label='Difference',
                        marker='o',
                        linewidth=0,
                        s=self.plot_marker_size)
        ax_hist.set_ylabel('Cosine similarity φ',
                           fontsize=self.plot_fontsize_large)
        ax_hist.set_xlabel('Reference time (min)',
                           fontsize=self.plot_fontsize_large)
        ax_hist.tick_params(axis='both', which='both',
                            labelsize=self.plot_fontsize_small)
        ax_hist.set_xlim(left=0, right=num_timepoints_reference)
        ax_hist.set_xticks(plot_x_ticks,
                           [str(x * plot_atp_min_correction)
                            for x in plot_x_ticks],
                           fontsize=self.plot_fontsize_small)
        ax_hist.set_ylim(-0.2, 1)

        ax_hist.spines['left'].set_position('zero')
        ax_hist.spines['bottom'].set_position('zero')
        ax_hist.xaxis.set_ticks_position('bottom')
        ax_hist.yaxis.set_ticks_position('left')

        lgnd = ax_hist.legend()
        for lgndHandle in lgnd.legendHandles:
            lgndHandle._sizes = [30]

        if kwargs.get("path_save", None) is not None:
            plt.savefig(kwargs["path_save"], dpi=self.plot_fig_dpi)
        plt.show()
        plt.close(fig)

    def plot_distribution_similarities(self,
                                       values_similarities,
                                       colors,
                                       labels,
                                       **kwargs):
        """Plot count of similarities as histogram."""
        bins = np.linspace(0, 1, 1000)
        plot_x_mins = list()
        plot_y_maxs = list()

        fig, axs = plt.subplots(dpi=self.plot_fig_dpi,
                                figsize=self.plot_fig_size)

        for i in range(len(values_similarities)):
            alpha = np.sqrt(1 / len(values_similarities))
            b = axs.hist(values_similarities[i],
                         bins=bins,
                         color=colors[i],
                         label=labels[i])
            # Append x position of the lowest bin to list
            for val_y in b[0]:
                if val_y != .0:
                    ind_x_min = list(b[0]).index(val_y)
                    break
            plot_x_mins.append(b[1][ind_x_min])
            # Append max. y-values to list
            plot_y_maxs.append(max(b[0]))

        plt.tick_params(axis='both',
                        which='both',
                        labelsize=self.plot_fontsize_small)

        plt.xlabel('Similarity values',
                   fontsize=self.plot_fontsize_large)
        plt.xlim(left=np.min(plot_x_mins) * 0.9,
                 right=1.01)
        #     plt.xticks([1 - b for b in np.logspace(start=np.min(plot_x_mins) * 0.9, stop=1, base=0.01, num=10)])
        plt.ylim(bottom=0,
                 top=np.max(plot_y_maxs) * 1.1)
        axs.set_xlabel('Similarity values',
                       fontsize=self.plot_fontsize_large)
        axs.set_ylabel('Density',
                       fontsize=self.plot_fontsize_large)
        plt.legend(fontsize=self.plot_fontsize_small)

        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'])
        plt.show()
        plt.close(fig)
