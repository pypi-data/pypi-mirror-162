import matplotlib.pyplot as plt
import matplotlib as mpl
plt.rcParams.update({'mathtext.fontset': 'cm'})
mpl.rcParams['text.usetex'] = True
mpl.rcParams['text.latex.preamble'] = r'\usepackage{{amsmath}}'

tex = r"$\frac{1}{2}$"
tex = r"$\frac{\partial}{\partial z}$"
tex = r'$\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}$'

fig = plt.figure(figsize=(10, 10), dpi=100)
t = fig.text(0, 0, tex, fontsize=30,
             verticalalignment="bottom", horizontalalignment="left",
             #bbox={'facecolor': 'white', 'edgecolor': 'red'}
             )

bbox = t.get_tightbbox(fig.canvas.get_renderer())
w, h = (bbox.width / 100 , bbox.height / 100 )

fig = plt.figure(figsize=(1.0*w, 1.0*h), dpi=300)
t = fig.text(0, 0, tex, fontsize=30,
             verticalalignment="bottom", horizontalalignment="left",
             )

fig.savefig("test.png")
plt.show()