import logging
from multiprocessing import Pool
from typing import Dict

import pyvista as pv
import treefiles as tf
from MeshObject import Mesh, Plotter
from tqdm import tqdm

from MeshAnim.time_series import TimeSeries


class Frames:
    def __init__(self, camera=None):
        self.time_series = []
        self.opt: Dict = {"smooth_shading": True}
        self.no_bar = False
        self.camera = camera

    def add_src(self, time_serie, **opts):
        self.time_series.append((time_serie, opts))
        if len(self.time_series) > 1:
            assert len(self.time_series[-2][0]) == len(self.time_series[-1][0])

    @property
    def n(self):
        if len(self.time_series) > 0:
            return len(self.time_series[0][0])

    def process_mesh(self):
        pass

    def set_scalar_bar_options(self, **kwargs):
        self.opt["scalar_bar_args"] = {**self.opt.get("scalar_bar_args", {}), **kwargs}

    def set_options(self, **kwargs):
        self.opt.update(kwargs)

    def screenshot(self, idx: int, fname: str, **kw):
        with Plotter(off_screen=True, size=(1000, 1000), **kw) as plotter:
            if self.camera:
                plotter.camera_position = self.camera
            for timeserie, opts in self.time_series:
                opts = dict(opts)
                time, mesh = timeserie[idx]
                if "callback" in opts:
                    opts.pop("callback")(plotter, time, mesh)
                # if "camera_position" in opts:
                #     plotter.camera_position = opts.pop("camera_position")
                plotter.add_mesh(
                    # opts.pop("method", lambda x: x.pv)(mesh), **{**self.opt, **opts}
                    mesh,
                    **{**self.opt, **opts},
                )
            if self.no_bar:
                plotter.remove_scalar_bar()
            plotter.screenshot(fname)  # , transparent_background=True)

    def generate_images(self, fname: str, parallel: bool = True):
        log.info(f"Generating screenshots to file://{tf.curDir(fname)}")

        if parallel:
            with Pool(min(20, self.n)) as p:
                p.starmap(
                    self.screenshot,
                    tqdm([(i, fname.format(i)) for i in range(self.n)], total=self.n),
                )
        else:
            for i in tqdm(range(self.n)):
                self.screenshot(i, fname.format(i))

    # def generate_images(
    #     self,
    #     camera,
    #     out_dir: tf.Tree = None,
    #     fname: str = None,
    #     no_bar: bool = None,
    #     s=np.s_[:],
    # ):
    #     view = type(camera).__name__
    #
    #     if no_bar is None:
    #         no_bar = self.no_bar
    #     if out_dir is None:
    #         out_dir = self.out_dir
    #     if fname is None:
    #         fname = out_dir.dir(view).dump().path("{}.png")
    #
    #     init_mesh = self.list_files[0]
    #     m = Object.load(init_mesh)
    #     mc = m.copy()
    #     mc.CellCenters()
    #     idx = np.where(mc.points.as_np()[:, 2] < m.BBCenter[2] + camera.height)
    #     arr = np.zeros(m.nbCells)
    #     arr[idx] = 1
    #
    #     init_camera(camera, init_mesh, self.geo_data)
    #     pas = self.dt * 1e3
    #     tQRS = self.tQRS * 1e3
    #
    #     for i, f in tqdm(enumerate(self.list_files[s]), total=len(self.list_files[s])):
    #         plotter = pv.Plotter(off_screen=True)
    #         plotter.camera_position = camera.get
    #         # mesh = pv.read(f)
    #         # clipped = camera.clipper.clip(mesh)
    #         m = Object.load(f)
    #         m.addCellData(arr, "tt")
    #         # m.write("out.vtk")
    #         # breakpoint()
    #         clipped = m.threshold((0.5, 1.5), "tt", method="cell", to_polydata=False)
    #         clipped = pv.wrap(clipped.data)
    #         plotter.add_mesh(clipped, **self.opt)
    #         if no_bar:
    #             plotter.remove_scalar_bar()
    #         plotter.screenshot(fname.format(i), transparent_background=True)
    #         plotter.close()
    #         # breakpoint()


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    root_ = tf.fTree(__file__, "out", "qwe")
    root_.file(j="meta.series")

    ts = TimeSeries.from_meta(root_.j)
    an = Frames()
    an.add_src(ts)
    an.add_src(ts)

    images_outdir = root_.dir("qwer").dump()
    an.generate_images(images_outdir.path("im_{}.png"))
