import rainbow as rb
import pandas as pd
import numpy as np

import os
import matplotlib.pyplot as plt
import matplotlib.image as mgimg
from matplotlib import animation


# Parse Agilent DAD.uv file
def create_dad_dataframe(path):
    dad = rb.agilent.chemstation.parse_uv(path)

    dad_matrix = np.asarray(dad.data)

    df_dad = pd.DataFrame(dad_matrix)
    df_dad.columns = dad.ylabels

    df_dad.insert(0, 'RT.min', dad.xlabels)

    return df_dad


# export retention time and absorption of dad
def export_wavelength(dad_df, wavelength, fn_out):

    subset = dad_df[["RT.min", wavelength]]
    subset.to_csv(fn_out, index=False, header=["RT", "DAD"], sep="\t")


# reshape intensity array to matrix
def intensity_matrix(df_dad1, wavelength, mod_time, sample_rate):

    run_time = np.round(df_dad1['RT.min'].values[-1], decimals=1)

    dim_x = int(np.floor(run_time / mod_time))
    dim_y = int(np.floor(mod_time * sample_rate))

    num_data = dim_x * dim_y

    intensity = df_dad1[wavelength].values

    # if less data points, then fill up with 0
    if num_data > len(intensity):
        intensity = np.append(intensity, np.zeros(num_data - len(intensity)))
    else:
        # cut off left over points
        intensity = intensity[0:num_data]

    raw_2d = np.reshape(intensity,
                        (dim_x, dim_y), order="C")

    return raw_2d, dim_x, dim_y


def shift_intensity_matrix(matrix, shift_time, sample_rate):

    shift_idx = int(np.round(sample_rate * shift_time, decimals=0))

    matrix_shifted = [None] * len(matrix)

    for n in range(len(matrix)):
        matrix_shifted[n] = np.roll(matrix[n], shift_idx)

    return matrix_shifted


def calc_axis(retention_time_array, dim_x, dim_y):
    run_time = np.round(retention_time_array[-1], decimals=0)
    y, x = np.meshgrid(retention_time_array[0:dim_y]*60, np.linspace(0, run_time, num=dim_x))

    return x, y


def plot2d(matrix, x, y, title, colormap, width, height, fn_out, inty_scale, bar_min=None, bar_max=None):

    if bar_min is None:
        bar_min = np.min(matrix)

    if bar_max is None:
        bar_max = np.max(matrix)

    fig, ax = plt.subplots(figsize=(width, height))

    c = ax.contourf(x, y, matrix, cmap=colormap,
                    vmin=bar_min,
                    vmax=bar_max, levels=500)
    ax.axis([x.min(), x.max(), y.min(), y.max()])
    ax.set_title(title)
    ax.set_xlabel('1D time [min]')
    ax.set_ylabel('2D time [s]')
    cbar = fig.colorbar(c, ax=ax)

    if inty_scale == 'relative':
        cbar.set_ticks([10, 20, 30, 40, 50, 60, 70, 80, 90])

    plt.savefig(fn_out, bbox_inches="tight")


def create_animation(plot_dir, width, height):

    list_of_im_paths = [plot_dir + "/" + f for f in os.listdir(plot_dir)
                        if f.endswith('.png')]

    fig = plt.figure(figsize=(width, height), dpi=300)
    plt.axis('off')

    # initiate an empty  list of "plotted" images
    myimages = []

    # loops through available png:s
    for fname in list_of_im_paths:
        # Read in picture
        img = mgimg.imread(fname)
        imgplot = plt.imshow(img)

        # append AxesImage object to the list
        myimages.append([imgplot])

    # create an instance of animation
    my_anim = animation.ArtistAnimation(fig, myimages, interval=500)

    path_out = plot_dir + "/all_plots.gif"
    my_anim.save(path_out)


