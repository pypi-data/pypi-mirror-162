import numpy as np
import matplotlib.colors as mcolors
import matplotlib.animation as animation
import pickle
from matplotlib import pyplot as plt
from matplotlib import colors
from numpy.ma import masked_where


def save_image_array(arr, name='save'):

    with open(name + '.pkl', 'wb') as f:
        pickle.dump(arr, f)


def open_image_array(file):

    with open(file, 'rb') as f:
        arr = pickle.load(f)
        return arr


def stack_cmaps(cmap, n_stacks):
    
    colors = np.array(cmap(np.linspace(0, 1, 200))) 
    
    for n in range(n_stacks - 1):
        colors = np.vstack((colors, cmap(np.linspace(0, 1, 200))))

    mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)

    return mymap


def image(res, cmap=plt.cm.hot, ticks='off',
          gamma=0.3, vert_exag=0, ls=[315, 10]):

    arr = res.image_array
    width = res.width_inches
    height = res.height_inches
    dpi = res.dpi

    w, h = plt.figaspect(arr)
    fig, ax0 = plt.subplots(figsize=(w, h), dpi=dpi)
    fig.subplots_adjust(0, 0, 1, 1)
    plt.axis(ticks)

    norm = colors.PowerNorm(gamma)
    light = colors.LightSource(azdeg=ls[0], altdeg=ls[1])
    
    if vert_exag != 0.0:
        ls = light.shade(arr, cmap=cmap, norm=norm, vert_exag=vert_exag, blend_mode='hsv')
        ax0.imshow(ls, origin='lower')
    else: 
        ax0.imshow(arr, origin='lower', cmap=cmap, norm=norm)

    fs = plt.gcf()
    fs.set_size_inches(width, height)

    return fig


def nebula_image(res_blue, res_green, res_red, ticks='off', gamma=1.0):

    arr_blue = res_blue.image_array
    width = res_blue.width_inches
    height = res_blue.height_inches
    dpi = res_blue.dpi
    arr_green = res_green.image_array
    arr_red = res_red.image_array

    arr_blue /= np.amax(arr_blue)
    arr_green /= np.amax(arr_green)
    arr_red /= np.amax(arr_red)

    final = np.dstack((arr_red, arr_green, arr_blue))

    w, h = plt.figaspect(arr_blue)
    fig, ax0 = plt.subplots(figsize=(w, h), dpi=dpi)
    fig.subplots_adjust(0, 0, 1, 1)
    plt.axis(ticks)
    fs = plt.gcf()
    fs.set_size_inches(width, height)
    ax0.imshow(final**gamma, origin='lower')

    return fig


def markus_lyapunov_image(res, gamma=1.0, ticks='off'):

    arr = res.image_array
    width = res.width_inches
    height = res.height_inches
    dpi = res.dpi
    red = np.zeros(arr.shape)

    green = np.zeros(arr.shape) + arr
    green[green > 0.0] = 0.0
    green[green < 0.0] -= np.amin(green)
    green /= np.amax(green)

    blue = np.zeros(arr.shape) + arr
    blue[blue < 0.0] = 0.0
    blue[blue > 0.0] -= np.amin(blue)
    blue /= np.amax(blue)

    final = np.dstack((red, green, blue))

    w, h = plt.figaspect(blue)
    fig, ax0 = plt.subplots(figsize=(width, height), dpi=dpi)
    fig.subplots_adjust(0, 0, 1, 1)
    plt.axis(ticks)
    fs = plt.gcf()
    fs.set_size_inches(width, height)
    ax0.imshow(final**gamma, origin='lower', vmin=0.0, vmax=1.0)

    return fig


def random_walk_image(res, cmap=plt.cm.hot, single_color=False, ticks='off', gamma=0.3,
                      vert_exag=0, ls=[315, 10], alpha_scale=1.0):

    arr = res.image_array
    width = res.width_inches
    height = res.height_inches
    dpi = res.dpi

    if single_color:
        arr[np.nonzero(arr)] = 1.0

    w, h = plt.figaspect(arr[:, :, 0])
    fig, ax0 = plt.subplots(figsize=(w, h), dpi=dpi)
    fig.subplots_adjust(0, 0, 1, 1)
    plt.axis(ticks)
    max_ind = float(arr.shape[-1] + 1)

    for i in range(arr.shape[-1]):
        
        im = arr[..., i]
        im = masked_where(im == 0, im)

        alpha = 1 - (i + 1)/max_ind
        alpha *= alpha_scale

        norm = colors.PowerNorm(gamma)
        light = colors.LightSource(azdeg=ls[0], altdeg=ls[1])

        if vert_exag != 0.0:
            ls = light.shade(im, cmap=cmap, vert_exag=vert_exag, blend_mode='overlay')
            ax0.imshow(ls, origin='lower', alpha=alpha, interpolation=None)
        else: 
            ax0.imshow(im, origin='lower', alpha=alpha, cmap=cmap, norm=norm, interpolation=None)
        
    fs = plt.gcf()
    fs.set_size_inches(width, height)
        
    return fig


def save_animation(series, fps=15, bitrate=1800, cmap=plt.cm.hot, filename='ani', ticks='off',
                   gamma=0.3, vert_exag=0, ls=[315, 10]):

    width = series[0].width_inches
    height = series[0].height_inches
    dpi = series[0].dpi

    fig = plt.figure()
    fig.subplots_adjust(0, 0, 1, 1)
    fs = plt.gcf()
    fs.set_size_inches(width, height)
    plt.axis(ticks)

    writer = animation.PillowWriter(fps=fps, metadata=dict(artist='Me'), bitrate=bitrate)
    norm = colors.PowerNorm(gamma)
    light = colors.LightSource(azdeg=ls[0], altdeg=ls[1])

    ims = []
    for s in series:

        arr = s.image_array
        ls = light.shade(arr, cmap=cmap, norm=norm, vert_exag=vert_exag, blend_mode='hsv')
        im = plt.imshow(ls, origin='lower', norm=norm)
        ims.append([im])

    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True, repeat_delay=1000)
    ani.save(filename + '.gif', dpi=dpi, writer=writer)
