import logging
from typing import Dict

import matplotlib.animation as animation
import matplotlib.image as mpimg
import numpy as np
import treefiles as tf
from tqdm import tqdm

from MeshAnim.time_series import TimeSeries


class Animate:
    def __init__(self, fname: str, clim=(0, 1)):
        self.axs = []
        self.fname = fname
        self.clim = clim
        self.opt: Dict = {"smooth_shading": True}

    def add_ax(self, glob: str, clim=None):
        if not clim:
            clim = self.clim
        self.axs.append(
            {
                "files": tf.fTree(glob).glob(tf.basename(glob)),
                "actors": [],
                "clim": clim,
            }
        )

    @tf.timer
    def animate(
        self, shape=(1, 1), dpi=400, figsize=None, fps=10, interval=100
    ) -> animation.FuncAnimation:
        """

        :param shape:
        :param dpi:
        :param figsize:
        :param fps: for saved animation
        :param interval: for displayed animation
        :return:
        """
        nrows, ncols = shape
        n_maxs = [len(x["files"]) for x in self.axs]
        n_max = np.max(n_maxs)

        fig, axs = tf.plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        for i, (ax, d) in enumerate(zip(np.ravel(axs), self.axs)):
            ax.set_aspect("equal")
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.spines["left"].set_visible(False)

            im = ax.imshow(mpimg.imread(d["files"][0]))
            im.set_clim(d["clim"])
            d["actors"].append(im)

        def update_img(i):
            for ax in self.axs:
                for x in ax["actors"]:
                    j = i if i < len(ax["files"]) else -1
                    x.set_data(mpimg.imread(ax["files"][j]))
            return [x["actors"] for x in self.axs]

        log.info(f"Starting to save {n_max} frames...")
        ani = animation.FuncAnimation(fig, update_img, n_max, interval=interval)
        writer = animation.writers["ffmpeg"](fps=fps)
        fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)

        with tqdm(total=n_max) as pbar:
            ani.save(
                self.fname,
                writer=writer,
                dpi=dpi,
                progress_callback=lambda *_: pbar.update(),
            )

        log.info(f"Wrote file://{self.fname}")
        return ani


def get_first(x):
    for i, y in enumerate(x):
        if y is None:
            return i
    log.error(x)


log = logging.getLogger(__name__)
logging.getLogger("PIL").setLevel(logging.INFO)
