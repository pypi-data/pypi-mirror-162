import matplotlib.pyplot as plt
plt.rcParams.update({'mathtext.fontset': 'cm'})
tex = r"$\frac{1}{2}$"
tex = r"$\frac{\partial}{\partial z}$"
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