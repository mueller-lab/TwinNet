import matplotlib as mpl
from matplotlib.colors import LightSource
from matplotlib.collections import PolyCollection
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd

from .tnautoregression import TNToolsAutoregression
from .tninference import TNToolsSimilarities

new_rc_params = {'text.usetex': False,
                 'svg.fonttype': 'none',
                 'lines.linewidth': 1}

mpl.rcParams.update(new_rc_params)


class TNToolsPlot:
    """
    This class is part of the toolset for usage of Twin Network (TN)
    on evaluation purposes.
    This part of the toolset is used to plot embedding similarities.
    """

    def __init__(self):
        self.plot_cmap = mpl.cm.get_cmap('viridis')
        self.plot_line_alpha_fg = 1
        self.plot_line_colors = ["#fde725",
                                 "#35b779",
                                 "#31688e",
                                 "#1f4696",
                                 "#ed1c24",
                                 '#6abd45'
                                 ]
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

        self.tools_autoregression = TNToolsAutoregression()
        self.tools_similarities = TNToolsSimilarities()

    def fn_similarity_self_cmap_custom(self, **kwargs):
        """
        Creates a colormap based on predefined
        'matplotlib' colormaps. Colors are adjusted
        such that color changes occur mainly in
        upper range of values.
        """
        samples = self.fn_similarity_self_cmap_custom_samples_exponential(
            **kwargs)
        list_colors = [self.plot_cmap(s) for s in samples]
        lscmap = mpl.colors.LinearSegmentedColormap.from_list("cmap_custom",
                                                              list_colors)
        return lscmap

    @staticmethod
    def fn_similarity_self_cmap_custom_samples_exponential(lamb=0.2,
                                                           **kwargs):
        """
        Generates 100 samples based on a
        decaying exponential distribution.
        """
        n_samples = 100
        xs = np.linspace(0, n_samples, n_samples)
        ys = np.exp(lamb * xs)
        ys = (ys - np.min(ys)) / (np.max(ys) - np.min(ys))

        grads = np.gradient(ys)
        tp_grad = next(grad for grad in grads if grad >= 1 / n_samples)
        x_tp_grad = np.where(np.isclose(grads, tp_grad))

        if kwargs.get("verbose", False):
            print(f"Index of change: {x_tp_grad[0] / n_samples}")

        return ys

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

    def plot_distribution_similarities_multiple(self,
                                                similarities,
                                                **kwargs):
        """
        Plot the distributions of the similarities at multiple indices
        of test image series.
        """
        # We have to un-nest the similarities for each timepoint first, as
        # the similarities are stored separately
        similarities_mean = [np.mean(_v_sim) for _v_sim in
                             similarities.values()]
        similarities_widths = [max(_v_sim) - min(_v_sim) for _v_sim in
                               similarities.values()]

        num_timepoints_reference = len(similarities_mean)

        plot_atp_min_correction = int(kwargs.get('intervals', 4))
        plot_colors = ["#431c53", '#1f4497']

        plot_x_ticks = list(range(0, num_timepoints_reference, 50))

        fig, axs = plt.subplots(1,
                                dpi=self.plot_fig_dpi,
                                figsize=self.plot_fig_size)
        axs.plot(range(len(similarities_mean)),
                 similarities_mean,
                 color=plot_colors[0],
                 linewidth=self.plot_line_width,
                 label="Similarity mean")
        axs.set_ylabel('Average cosine similarity φ',
                       fontsize=self.plot_fontsize_large)
        axs.set_xlabel('Acquisition time (min)',
                       fontsize=self.plot_fontsize_large)
        axs.tick_params(axis='both',
                        which='both',
                        labelsize=self.plot_fontsize_small)
        axs.set_xlim(left=0,
                     right=num_timepoints_reference)
        axs.set_xticks(plot_x_ticks,
                       [str(x * plot_atp_min_correction)
                        for x in plot_x_ticks],
                       fontsize=self.plot_fontsize_small)

        axs2 = plt.twinx()
        axs2.plot(range(len(similarities_mean)),
                  similarities_widths,
                  color=plot_colors[1],
                  linewidth=self.plot_line_width,
                  label='Similarity range')
        axs2.grid(False)
        axs2.tick_params(axis='both',
                         which='both',
                         labelsize=self.plot_fontsize_small)
        axs2.set_ylabel('Similarity distribution range',
                        fontsize=self.plot_fontsize_large)
        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'])
        plt.show()
        plt.close()

    def plot_distribution_stages_dev_fractions(self,
                                               values_histograms,
                                               num_timepoints_reference,
                                               colors,
                                               labels,
                                               **kwargs):
        """
        Plot a histogram to show where the
        predictions for an acquisition timepoint lie.
        """
        plot_atp_min_correction = int(kwargs.get('intervals', 4))
        plot_x_ticks = list(range(0, num_timepoints_reference, 50))
        bins = list(range(0, num_timepoints_reference))

        fig, ax_hist = plt.subplots(dpi=self.plot_fig_dpi,
                                    figsize=self.plot_fig_size)
        for i in range(len(values_histograms)):
            alpha = np.sqrt(self.plot_line_alpha_fg / len(values_histograms))
            counts, bins = np.histogram(values_histograms[i], bins=bins)
            plt.hist(bins[:-1], bins,
                     alpha=self.plot_line_alpha_fg,
                     color=colors[i] + (alpha,),
                     label=labels[i],
                     weights=[c / sum(counts) * 100 for c in counts])

        ax_hist.set_ylabel('Percentage of predictions',
                           fontsize=self.plot_fontsize_large)
        ax_hist.set_xlabel('Predicted reference developmental time (min)',
                           fontsize=self.plot_fontsize_large)
        ax_hist.tick_params(axis='both',
                            which='both',
                            labelsize=self.plot_fontsize_small)
        ax_hist.set_xlim(left=0, right=num_timepoints_reference)
        ax_hist.set_xticks(plot_x_ticks,
                           [str(x * plot_atp_min_correction)
                            for x in plot_x_ticks],
                           fontsize=self.plot_fontsize_small)
        plt.legend()
        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'])
        plt.show()

        plt.close()

    def plot_similarity_self_2d(self, similarities, **kwargs):
        """
        Plot similarities of images from a time-series image sequence
        of an embryo to earlier images from the same series as
        two-dimensional matrix.

        Parameters
        ----------
        similarities: list
            List of lists with similarity values. Each sublist contains
            similarity values between one test image and all earlier
            images in the test sequence. Thus, the number of similarities
            must be number of time points in the acquisition - 1.
        **kwargs: Variable keyword arguments
            See below.

        Keyword Arguments
        -----------------
        intervals: int/float
            Time intervals (min), at which test embryo images
            were acquired. Default is 4 minutes. Use this
            to adjust axis labels to be labelled with minutes.
        """
        num_imgs_test = len(similarities) + 1
        plot_atp_min_correction = int(kwargs.get('intervals', 4))
        plot_xy_ticks = list(range(0, num_imgs_test, 50))

        if kwargs.get("color_adjust", False):
            plot_colors_hlf = self.fn_similarity_self_cmap_custom(**kwargs)
        else:
            plot_colors_hlf = self.plot_cmap

        xs_grid, ys_grid, zs_grid_plot = self.tools_autoregression.\
            fn_2d_sims_to_arrays(
                similarities,
                num_imgs_test,
                square=True
            )

        # Figure
        f, ax = plt.subplots(dpi=self.plot_fig_dpi,
                             figsize=self.plot_fig_size_square)
        f.tight_layout(rect=[0.0, 0.00, 0.8, 1.0])

        # Plot
        ax.imshow(zs_grid_plot,
                  cmap=plot_colors_hlf)

        # Labels and titles
        ax.tick_params(axis='both',
                       which='both',
                       labelsize=self.plot_fontsize_small)
        ax.set_xlabel('Time (min)',
                      fontsize=self.plot_fontsize_large)
        ax.set_ylabel('Time (min)',
                      fontsize=self.plot_fontsize_large)
        ax.set_xlim(left=0,
                    right=len(similarities))
        ax.set_ylim(bottom=0,
                    top=len(similarities))
        ax.set_xticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction)
                       for a in plot_xy_ticks],
                      fontsize=self.plot_fontsize_small)
        ax.set_yticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction)
                       for a in plot_xy_ticks],
                      fontsize=self.plot_fontsize_small)

        divider = make_axes_locatable(ax)
        sm = plt.cm.ScalarMappable(cmap=plot_colors_hlf)
        cax = divider.append_axes("right",
                                  size="5%",
                                  pad=0.05)
        cax.tick_params(axis='both',
                        which='both',
                        labelsize=self.plot_fontsize_small)
        cbar = f.colorbar(sm,
                          cmap=plot_colors_hlf,
                          cax=cax)
        cbar.ax.set_ylabel('Cosine similarity ϕ',
                           fontsize=self.plot_fontsize_large)

        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'])
        else:
            plt.show()
        plt.close()

    def plot_similarity_self_3d(self,
                                similarities,
                                **kwargs):
        """
        Plot similarities of images from a time-series image sequence
        of an embryo to earlier images from the same series as
        three-dimensional surface plot.

        Parameters
        ----------
        similarities: list
            List of lists with similarity values. Each sublist contains
            similarity values between one test image and all earlier
            images in the test sequence. Thus, the number of similarities
            must be number of time points in the acquisition - 1.
        **kwargs: Variable keyword arguments
            See below.

        Keyword Arguments
        -----------------
        intervals: int/float
            Time intervals (min), at which test embryos
            were acquired. Default is 4 minutes. Use this
            to adjust axis labels to minute.
        plot_index: int
            Index of the last image that should be included in the plot.
            We assume 1-based indexing for indexing of the images. Thus,
            the lowest image index that can be given is 2, as the first
            comparison between two images is between images at indices
            2 and 1.
        rotation_angle: int
            Rotation of plot along z-axis.
        """
        # Number of images in the dataset is by 1 lager
        # than number of similarities
        num_imgs_test = len(similarities) + 1
        # This is the index of the image until which similarities
        # should be plotted.
        plot_index = kwargs.get("plot_index", len(similarities))

        print(f"[INFO] Number of similarity lists: {len(similarities)}")

        assert num_imgs_test >= plot_index >= 2, \
            f"Plot index is wrong." \
            f"\nLowest plot index is 2, " \
            f"as first comparison is image nr. 2 vs. image nr. 1. " \
            f"\nHighest plot index is {num_imgs_test}, " \
            f"as this is the number of images in the dataset."

        # Plot parameters
        plot_alpha_polygon = 0.5
        plot_atp_min_correction = int(kwargs.get('intervals', 4))
        plot_bottom = 0.0
        plot_color_line_marker = self.plot_line_colors[5]
        plot_color_polygon = plot_color_line_marker
        plot_grid_linewidth = 0.5
        plot_tick_pad = -2
        plot_xy_ticks = list(range(0, num_imgs_test, 50))

        mpl.rcParams.update({'axes.linewidth': plot_grid_linewidth,
                             'grid.linewidth': plot_grid_linewidth,
                             'xtick.major.width': plot_grid_linewidth,
                             'xtick.major.pad': plot_tick_pad,
                             'ytick.major.width': plot_grid_linewidth,
                             'ytick.major.pad': plot_tick_pad})

        # We used 1-indexing for the image indices and the number of
        # similarities is supposed to be 1 smaller than the number of
        # images. Thus, we can slice the array of similarities until
        # plot_index - 1 (will be excluded from slice). As a result,
        # the last list of similarities shown here corresponds to
        # similarities[plot_index - 2], which can be used to plot a
        # line at the edge.
        xs_grid, ys_grid, zs_grid_plot, zs_grid_colors = \
            self.tools_autoregression.fn_3d_sims_to_arrays(
                similarities[:plot_index - 1],
                num_imgs_test
            )

        # Figure
        fig = plt.figure(dpi=self.plot_fig_dpi,
                         figsize=self.plot_fig_size)
        spec = gridspec.GridSpec(figure=fig,
                                 ncols=2,
                                 nrows=1,
                                 width_ratios=[1, 0.05])
        ax = fig.add_subplot(spec[0, 0],
                             projection='3d')
        cax = fig.add_subplot(spec[0, 1])

        scatter = ax.plot_surface(xs_grid, ys_grid, zs_grid_plot,
                                  cmap=self.plot_cmap,
                                  edgecolors=(1., 1., 1., 1.),
                                  alpha=1.0,
                                  linewidth=0,
                                  antialiased=False,
                                  shade=False)

        # Set axis range
        xlim_max = ax.get_xlim()[1]
        ylim_min = ax.get_ylim()[0]
        zlim_min = -0.017

        if kwargs.get("plot_line", False):
            line_x, line_y, line_z = \
                self.tools_autoregression.fn_3d_sims_line_plot(
                    similarities,
                    plot_index
                )

            # Line plots
            ax.plot(line_x, line_y, line_z,
                    color=plot_color_line_marker,
                    linewidth=self.plot_line_width,
                    zorder=10)

            vertices = [self.tools_autoregression.fn_polygon_under_graph(
                line_y,
                line_z,
                zlim_min
            )]

            poly = PolyCollection(
                vertices,
                facecolors=[plot_color_polygon]*len(vertices),
                alpha=plot_alpha_polygon
            )

            ax.add_collection3d(poly,
                                zs=[plot_index],
                                zdir='x')

            # Line orthogonal to x-axis
            ax.plot([plot_index, plot_index],
                    [ylim_min, plot_index],
                    [zlim_min, zlim_min],
                    color=plot_color_line_marker,
                    linewidth=self.plot_line_width)
            # Line orthogonal to y-axis
            ax.plot([plot_index, xlim_max],
                    [plot_index, plot_index],
                    [zlim_min, zlim_min],
                    color=plot_color_line_marker,
                    linewidth=self.plot_line_width)
            # Line parallel to z-axis
            ax.plot([plot_index, plot_index],
                    [plot_index, plot_index],
                    [zlim_min, similarities[plot_index - 2][-1]],
                    color=plot_color_line_marker,
                    linewidth=self.plot_line_width)

        # Labels and titles
        ax.tick_params(axis='both',
                       which='both',
                       labelsize=self.plot_fontsize_small)
        ax.set_xlabel('Time (min)',
                      fontsize=self.plot_fontsize_large)
        ax.set_ylabel('Time (min)',
                      fontsize=self.plot_fontsize_large)
        ax.set_zlabel('Cosine similarity ϕ',
                      fontsize=self.plot_fontsize_large)
        ax.set_xlim3d(left=0,
                      right=len(similarities))
        ax.set_xticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction)
                       for a in plot_xy_ticks],
                      fontsize=self.plot_fontsize_small)
        ax.set_yticks(plot_xy_ticks,
                      [str(a * plot_atp_min_correction)
                       for a in plot_xy_ticks],
                      fontsize=self.plot_fontsize_small)
        ax.set_ylim3d(bottom=0,
                      top=len(similarities))
        ax.set_zlim3d(bottom=plot_bottom,
                      top=1.0)

        # Colorbar
        scatter.set_clim(0.0, 1.0)
        cax.set_ylim(bottom=0.0, top=1.0)
        cax.set_yticks(list(np.arange(0, 1, 0.1)),
                       list(np.arange(0, 1, 0.1)),
                       fontsize=self.plot_fontsize_small)
        cax.tick_params(pad=-plot_tick_pad)
        cbar = plt.colorbar(scatter,
                            cax=cax,
                            format='%.1f',
                            fraction=0.05,
                            )
        cbar.set_label(label="Cosine similarity ϕ",
                       size=self.plot_fontsize_large,)
        cax.set_aspect(10)

        if isinstance(kwargs.get('rotation_angle', None), int):
            ax.view_init(
                25,
                int(kwargs.get('rotation_angle', -60))
            )

        if 'path_save' in kwargs:
            plt.savefig(kwargs['path_save'])
        else:
            plt.show()
        plt.close()

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
        -----------------
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
        duration_query = num_timepoints_query * \
                         plot_atp_min_correction_x
        duration_reference = num_timepoints_reference * \
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

    def plot_similarity_zscores_inbatch(self, similarities, **kwargs):
        """
        Plot calculated similarities of multiple embryos in one batch
        for multiple image indices of these embryos.

        Parameters
        ----------
        similarities: pandas.core.frame.DataFrame
            A pandas DataFrame containing similarity values
            or zscores. Values should be sorted by embryo
            names (column names) and image indices (row indices).
        **kwargs: Variable keyword arguments
            See below.

        Keyword Arguments
        -----------------
        intervals_x: int/float
            Time intervals (min), at which test embryo
            images were acquired. Default is 4 minutes.
        """
        columns_embryos = list(similarities.columns)
        num_embryos = len(columns_embryos)
        num_indices = len(similarities.index)

        plot_atp_min_correction = kwargs.get("intervals_x", 2)
        plot_xs = list(range(1, num_indices + 1))
        plot_x_ticks = list(range(0, num_indices, 50))

        fig, ax = plt.subplots(1,
                               dpi=self.plot_fig_dpi,
                               figsize=self.plot_fig_size)

        for column_embryo in columns_embryos:
            color = self.plot_cmap(
                columns_embryos.index(column_embryo) / num_embryos)

            ax.scatter(plot_xs,
                       similarities[column_embryo],
                       alpha=self.plot_line_alpha_fg,
                       c=[color] * len(plot_xs),
                       label=column_embryo,
                       linewidth=self.plot_line_width,
                       marker='o',
                       s=self.plot_line_width
                       )

        ax.set_xlabel('Time (min)',
                      fontsize=self.plot_fontsize_large)
        ax.set_xticks(plot_x_ticks,
                      [str(x * plot_atp_min_correction)
                       for x in plot_x_ticks],
                      fontsize=self.plot_fontsize_small)
        ax.set_xlim(left=0,
                    right=num_indices)
        ax.set_ylabel('Cumulative z-score',
                      fontsize=self.plot_fontsize_large)
        ax.tick_params(axis='both',
                       which='both',
                       labelsize=self.plot_fontsize_small)
        ax.legend(fontsize=self.plot_fontsize_small,
                  ncol=2)
        if kwargs.get('path_save', None) is not None:
            _ = plt.savefig(kwargs['path_save'],
                            dpi=300)
        plt.show()
        plt.close(fig)
