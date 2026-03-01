import numpy as np

def symlog(data):
    idx_pos = np.where(data > 0)
    idx_neg = np.where(data < 0)
    data_symlog = np.zeros((data.shape[0], data.shape[1]))
    data_symlog[:] = np.nan
    data_symlog[idx_pos] = np.log(data[idx_pos])
    data_symlog[idx_neg] = -np.log(-data[idx_neg])
    return data_symlog

def annotate_heatmap(array_2D, ax, ndecimals=2, fontsize=8):
    for (j,i),label in np.ndenumerate(array_2D):
        if ndecimals==0 and ~np.isnan(label):
            label = int(label)
        else:
            label = round(label,ndecimals)
        ax.text(i,j,label,ha='center',va='center', color='0.8', fontsize=fontsize, fontweight='bold')


def heatmap(array, c='viridis', ax=None, cbar_kw={}, cbarlabel="", datamin=None, datamax=None, logscale_cmap=False,
            annotate=None, row_labels=None, col_labels=None, show_gridlines=True, fontsize=8):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    if not ax:
        ax = plt.gca()
    cmap = getattr(plt.cm, c)

    # get array size and xy labels
    data = array.astype(float)
    ny, nx = data.shape

    # get row and column labels
    if row_labels is None:
        row_labels = list(np.arange(ny) + 1)
    if col_labels is None:
        col_labels = list(np.arange(nx) + 1)

    # get locations of nan values and negative values, replace values so these don't trigger an error
    naninds = np.where(np.isnan(data) == True)
    infinds = np.where(np.isinf(data) == True)
    if len(infinds[0]) > 0:
        data[infinds] = np.nan
    if len(naninds[0]) > 0:
        data[naninds] = np.nanmean(data)
    if len(infinds[0]) > 0:
        data[infinds] = np.nanmean(data)
    data_cmap = data.copy()

    # get min and max values
    if datamin is None:
        datamin = np.nanmin(data_cmap)
    if datamax is None:
        datamax = np.nanmax(data_cmap)

    # get colormap to plot
    if logscale_cmap:  # plot on logscale
        data_cmap = symlog(data_cmap)
        datamin, datamax = np.min(data_cmap), np.max(data_cmap)

    # get cmap gradations
    dataint = (datamax - datamin) / 100
    norm = plt.Normalize(datamin, datamax + dataint)
    # convert data array into colormap
    colormap = cmap(norm(data_cmap))

    # Set the positions of nan values in colormap to 'lime'
    colormap[naninds[0], naninds[1], :3] = 0, 1, 0
    colormap[infinds[0], infinds[1], :3] = 1, 1, 1

    # plot colormap
    im = ax.imshow(colormap, interpolation='nearest')

    # Create colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.07)
    cbar = ax.figure.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)

    if logscale_cmap == True:
        cbar_labels = cbar.ax.get_yticks()
        cbar.set_ticks(cbar_labels)
        cbar_labels_unlog = list(np.round(np.exp(np.array(cbar_labels)), 2))
        cbar.set_ticklabels(cbar_labels_unlog)

    # Turn off gridlines if required
    ax.tick_params(axis='both', which='both', length=0, gridOn=show_gridlines)

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels, fontsize=fontsize, ha="right")
    ax.set_yticklabels(row_labels, fontsize=fontsize)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=False, bottom=True,
                   labeltop=False, labelbottom=True)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=90,
             rotation_mode="anchor")

    # Annotate
    if annotate is not None:
        if isinstance(annotate, int):
            ndecimals = annotate
        else:
            ndecimals = 3
        annotate_heatmap(array, ax, ndecimals=ndecimals, fontsize=fontsize)

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    # set xticks
    ax.set_xticks(np.arange(data.shape[1] + 1) - .5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - .5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=0.5)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar, ax

def plot_variant_heatmap(arr, seq, N_res_per_heatmap_row, aaList, seq_name=None, savefig=None, figtitle=None, width_per_res=4):
    import matplotlib.pyplot as plt
    # Visualize the heatmaps
    seq_len = len(seq)
    residue_num = list(np.arange(1, seq_len + 1))
    num_heatmaps = int(np.ceil(seq_len / N_res_per_heatmap_row))
    heatmap_min = np.min(arr)
    heatmap_max = np.max(arr)
    fig, ax = plt.subplots(num_heatmaps, 1, figsize=(N_res_per_heatmap_row / len(aaList) * width_per_res, num_heatmaps * 4))
    for k in range(num_heatmaps):
        if num_heatmaps == 1:
            ax_k = ax
        else:
            ax_k = ax[k]
        residue_num_k = residue_num[k * N_res_per_heatmap_row:min((k + 1) * N_res_per_heatmap_row, seq_len)]
        start_idx = k * N_res_per_heatmap_row
        end_idx = min((k + 1) * N_res_per_heatmap_row, seq_len)
        heatmap_k = arr[:, start_idx:end_idx]
        wt_idxs_k = np.array([[aaList.index(wt_aa),res_idx] for res_idx, wt_aa in enumerate(seq[start_idx:end_idx])])
        im = ax_k.imshow(heatmap_k, cmap="viridis", aspect="auto", vmin=heatmap_min, vmax=heatmap_max)
        ax_k.scatter(wt_idxs_k[:,1], wt_idxs_k[:,0], c='r', s=4)
        ax_k.set_yticks(range(20), aaList)
        ax_k.set_xticks(range(len(residue_num_k)), residue_num_k, fontsize=7, rotation=45)
    fig.colorbar(im, orientation='vertical')
    if figtitle is not None:
        if seq_name is not None:
            figtitle = seq_name + ': ' + figtitle
        plt.suptitle(figtitle, y=0.93, fontsize=16)
    if savefig is not None:
        plt.savefig(savefig, dpi=300, bbox_inches='tight')
    plt.show()
