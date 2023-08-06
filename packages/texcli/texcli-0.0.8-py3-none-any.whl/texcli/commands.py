import sys

import matplotlib.pyplot as plt


def latex(tex, output_file, dpi=300, bgcolor='white', fgcolor='black'):
    tex = '$ ' + tex + ' $'

    plt.rcParams.update({'mathtext.fontset': 'cm'})
    fig = plt.figure(figsize=(10, 10), dpi=100)

    t = fig.text(0, 0, tex,
                horizontalalignment='left', verticalalignment='bottom',
                fontsize=30
                )

    r = fig.canvas.get_renderer()

    bbox = t.get_tightbbox(r)
    w, h = (bbox.width / r.dpi, bbox.height / r.dpi)

    fig = plt.figure(figsize=(1.1 * w, 1.1 * h), dpi=dpi)
    t = fig.text(0, 0, tex, fontsize=30,
                 verticalalignment="bottom", horizontalalignment="left",
                 bbox={'facecolor': bgcolor, 'edgecolor': bgcolor},
                 color=fgcolor
                 )

    fig.savefig(output_file, transparent=False)


if __name__ == '__main__':
    latex(r'\frac{\partial}{\partial z}', 'test.png')
