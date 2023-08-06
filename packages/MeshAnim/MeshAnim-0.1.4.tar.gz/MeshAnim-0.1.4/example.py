import logging

import numpy as np
import treefiles as tf
from MeshObject import Object

from MeshAnim.animate import Animate
from MeshAnim.frames import Frames
from MeshAnim.time_series import TimeSeries


@tf.timer
def main():
    man = Manager(tf.fTree(__file__, "out"), split=1)
    man.generate_meshes()
    man.generate_frames()
    man.animate()


class Manager:
    def __init__(self, path, split: int = 0):
        self.root = tf.Tree(path)
        self.root.file(
            out="output.mp4", m_mesh="meta_mesh.series", m_split="meta_splitted.series"
        )
        self.root.dir(d_mesh="meshes").file(m="mesh_{}.vtk")
        self.root.dir(d_frame="frames").file(m="frame_{}.png")
        self.split = split

    def generate_meshes(self):
        self.root.d_mesh.dump(clean=True)
        writer = TimeSeries()
        radi, dt = np.linspace(1, 5, 10), 5e-3
        for i, r in enumerate(radi):
            m = Object.Sphere(SetRadius=r)
            m.transform(scale=[1, 1, 1 + i / 10])
            writer.add_file(i * dt, self.root.d_mesh.m.format(i), m)
        writer.write(self.root.m_mesh)

        if self.split:
            out = self.root.d_mesh.dir("split").dump(clean=True)
            out.file(m=tf.basename(self.root.d_mesh.m))

            r = TimeSeries.from_meta(self.root.m_mesh)
            r = r.split(n=self.split, out=out.m, meta_fname=self.root.m_split)

            for t, m in r:
                m.addPointData(np.ones(m.nbPoints) * t, "time (s)")
                m.addPointData(-np.ones(m.nbPoints) * t, "timer (s)")
                m.write()  # overwrite

    def generate_frames(self):
        meta = self.root.m_split if self.split else self.root.m_mesh
        serie_1 = TimeSeries.from_meta(meta)
        an = Frames()
        an.set_options(show_edges=True)
        an.set_scalar_bar_options(color="black")
        an.add_src(
            serie_1,
            scalars="timer (s)",
            clim=serie_1.range("timer (s)"),
            callback=add_text_callback,
        )

        self.root.d_frame.dump(clean=True)
        an.generate_images(self.root.d_frame.m)

    def animate(self):
        an = Animate(self.root.out)
        an.add_ax(self.root.d_frame.m.format("*"))
        an.add_ax(self.root.d_frame.m.format("*"))
        an.animate(shape=(1, 2), fps=20, figsize=(8, 4))


def add_text_callback(p, t, m):
    p.add_text(f"time: {round(t*1e3, 2)}ms", color="black", font_size=10)


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    main()
