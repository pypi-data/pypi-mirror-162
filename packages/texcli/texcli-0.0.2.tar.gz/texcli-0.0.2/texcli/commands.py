import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from skimage.io import imread, imsave

def latex(tex, output_file):
    tex = '$ ' + tex.strip() + ' $'

    plt.rcParams.update({'mathtext.fontset': 'cm'})
    fig = plt.figure(figsize=(30, 30))

    ax = fig.add_axes([0, 0, 1, 1])
    #ax.patch.set_facecolor('#ff0000')
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)

    t = ax.text(0, 0, tex,
                horizontalalignment='left', verticalalignment='bottom', fontsize=24)

    fig.savefig(output_file, transparent=False)

    img = imread(output_file)

    min_row = np.min(np.where(img == 0)[0]) - 5
    max_col = np.max(np.where(img == 0)[1]) + 5

    cropped = img[min_row:, :max_col, :]
    imsave(output_file, cropped)


if __name__ == '__main__':
    latex(r'\Delta x^2', 'test.png')
