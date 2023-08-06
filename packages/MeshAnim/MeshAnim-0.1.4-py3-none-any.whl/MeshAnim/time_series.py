import logging
from typing import NamedTuple, List, Union

import numpy as np
import treefiles as tf
from MeshObject import Mesh, TMeshLoadable


class Serie(NamedTuple):
    time: float
    mesh: Mesh


class TimeSeries:
    def __init__(
        self,
        files: List[str] = None,
        times: List[float] = None,
        root: Union[tf.Tree, str] = None,
    ):
        if not files:
            files = []
        self.files = files
        if not times:
            times = []
        self.times = times

        self.root = None
        if not root and len(self.files) > 0:
            self.root = tf.fTree(self.files[0])
        self.check()
        self._dt = None

    @property
    def dt(self):
        return self._dt

    @dt.setter
    def dt(self, x: float):
        self._dt = x
        try:
            self.times = [i * x for i in range(len(self))]
        except ValueError:
            self.times = None

    def __repr__(self):
        return f"TimeSeries [{self.root.abs()}]"

    @classmethod
    def from_glob(cls, fname: str, dt=1):
        c = cls(files=tf.fTree(fname).glob(tf.basename(fname)))
        c.dt = dt
        return c

    @classmethod
    def from_meta(cls, fname):
        if isinstance(fname, tf.Tree):
            fname = fname.path("meta")
        fname = tf.ensure_ext(fname, "series")
        r = tf.curDir(fname)
        data = load_json(fname)["files"]
        files = [tf.join(r, x["name"]) for x in data]
        times = [x["time"] for x in data]
        return cls(files, times)

    @classmethod
    def from_dir(cls, obj: tf.TS):
        obj = tf.Tree(obj)
        g = obj.glob("*.series")
        if len(g) == 0:
            raise FileNotFoundError(f"meta.series not found in {obj.abs()}")
        return cls.from_meta(g[0])

    @property
    def basenames(self):
        return [tf.basename(x) for x in self.files]

    def __len__(self):
        return len(self.files)

    def __getitem__(self, item) -> Serie:
        return Serie(self.times[item], Mesh.load(self.files[item]))

    def check(self):
        for x in self.files:
            if not tf.isfile(x):
                log.error(f"File not found: {x}")

        for a, b in zip(self.files, self.basenames):
            assert a == self.root.path(b), f"{a} != {self.root.path(b)}"

    def add_file(self, time: float, name: str, mesh: Mesh = None):
        self.files.append(name)
        self.times.append(time)
        if mesh:
            mesh.write(name)

    def rm_abs(self, x: str):
        return x.replace(f"{self.root.abs()}/", "")

    def write(self, fname=None):
        if not fname:
            fname = tf.curDirs(self.files[0], "meta")
        fname = tf.ensure_ext(fname, "series")
        self.root = tf.fTree(fname)
        meta = {
            "file-series-version": "1.0",
            "files": [
                {"name": self.rm_abs(a), "time": b}
                for a, b in zip(self.files, self.times)
            ],
        }
        dump_json(fname, meta)
        log.info(f"Wrote meta file to file://{fname}")
        return self

    def split(self, n, out, meta_fname=None):
        out = tf.Str(out)
        out.parent.dump()
        log.info(f"Start splitting to {out}")

        class K:
            _k = -1

            @staticmethod
            def __call__(*args, **kwargs):
                K._k += 1
                return K._k

        k = K()
        new_ts = TimeSeries()
        m0 = Mesh.load(self.files[0])
        x0, t0 = m0.points.as_np(), self.times[0]
        new_ts.add_file(t0, out.f(k()), m0)
        for i in range(1, len(self)):
            m1 = Mesh.load(self.files[i])
            x1, t1 = m1.points.as_np(), self.times[i]

            dx = (x1 - x0) / (n + 1)
            dt = (t1 - t0) / (n + 1)
            for j in range(1, n + 1):
                m = m1.copy()
                m.points = x0 + j * dx
                new_ts.add_file(t0 + j * dt, out.f(k()), m)

            new_ts.add_file(t1, out.f(k()), m1)
            x0, t0 = x1, t1
        new_ts.write(meta_fname)
        return new_ts

    def range(self, array_name):
        rgs = []
        for x in self.files:
            arr = Mesh.load(x).getPointDataArray(array_name)
            rgs.append((np.min(arr), np.max(arr)))
        rgs = np.array(rgs)
        return np.min(rgs[:, 0]), np.max(rgs[:, 1])

    @classmethod
    def from_point_data(cls, filename: str, array_name: str, dt=1):
        return StaticTimeSeries(filename, array_name, dt)

    @classmethod
    def from_mesh(cls, obj: TMeshLoadable, array_name: str, dt=1):
        return StaticTimeSeries2(obj, array_name, dt)

    def compute_dt(self):
        dts = [self.times[i+1]-self.times[i] for i in range(len(self)-1)]
        self._dt = np.mean(dts)


class StaticTimeSeries(TimeSeries):
    def __init__(self, filename: str, array_name: str, dt=5e-3):
        super().__init__([filename])
        self.array_name = array_name
        self.mesh = Mesh.load(filename)
        self.dt = dt
        r0 = self.range(self.array_name)[0]
        for i in range(len(self)):
            self.times[i] += r0

    def __getitem__(self, item) -> Serie:
        m = self.mesh.copy()
        m[self.array_name][np.where(m[self.array_name] > self.times[item])] = np.nan
        return Serie(self.times[item], m)

    def __len__(self):
        r = self.range(self.array_name)
        return int(r[1] - r[0] / self.dt + 2)


class StaticTimeSeries2(TimeSeries):
    def __init__(self, obj: TMeshLoadable, array_name: str, dt=5e-3):
        super().__init__()
        self.array_name = array_name
        self.mesh = Mesh.load(obj)
        self.dt = dt
        r0 = self.range()[0]
        for i in range(len(self)):
            self.times[i] += r0

    def __getitem__(self, item) -> Serie:
        m = self.mesh.copy()
        # m[self.array_name][np.where(m[self.array_name] > self.times[item])] = np.nan
        return Serie(None, m)

    def __len__(self):
        r = self.range()
        return int(r[1] - r[0] / self.dt + 2)

    def range(self):
        arr = self.mesh.getPointDataArray(self.array_name)
        arr = np.nan_to_num(arr)
        if len(arr)>0:
            return arr.min(), arr.max()
        else:
            return 0, 1


def load_json(*a, **b):
    return tf.load_json(*a, **{**b, **{"force_ext": False}})


def dump_json(*a, **b):
    return tf.dump_json(*a, **{**b, **{"force_ext": False}})


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    root_ = tf.fTree(__file__, "out", dump=True, clean=True)
    root_.file(j="mesh.vtu.series")
    root_.dir("qwe").dump().file(m="mesh_{}.vtk")

    w = TimeSeries()
    radi, dt = np.linspace(1, 2, 10), 5e-3
    for i, r in enumerate(radi):
        m = Mesh.Sphere(SetRadius=r)
        w.add_file(i * dt, root_.qwe.m.format(i), m)
    w.write(root_.j)

    r = TimeSeries.from_meta(root_.j)
    r = r.split(
        n=1,
        out=root_.qwe.dir("test").dump().path("mesh_{}.vtk"),
        meta_fname=root_.qwe.path("meta"),
    )

    for t, m in r:
        arr = np.zeros(m.nbPoints)
        # process `arr`
        m.addPointData(arr, "array name")
        m.write()  # overwrite
