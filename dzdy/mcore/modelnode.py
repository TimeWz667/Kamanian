from abc import ABCMeta, abstractmethod
from dzdy.mcore.request import *

__author__ = 'TimeWz667'


class AbsModel(metaclass=ABCMeta):
    def __init__(self, name, meta=None):
        self.Meta = meta
        self.Name = name
        self.Requests = RequestSet()
        self.TimeEnd = None

    def initialise(self, ti=None, y0=None):
        if y0:
            self.read_y0(y0, ti)
        self.reset(ti)
        self.drop_next()

    def reset(self, ti):
        pass

    def read_y0(self, y0, ti):
        pass

    def listen(self, src_model, src_value, src_target):
        pass

    @property
    def next(self):
        if self.Requests.is_empty():
            self.find_next()
        return self.Requests.Requests

    @property
    def tte(self):
        return self.Requests.Time

    def drop_next(self):
        self.Requests.clear()

    @abstractmethod
    def find_next(self):
        pass

    @abstractmethod
    def fetch(self, rs):
        pass

    @abstractmethod
    def exec(self):
        pass

    @abstractmethod
    def do_request(self, req):
        pass

    @abstractmethod
    def observe(self, ti):
        pass

    @abstractmethod
    def output(self):
        pass

    @abstractmethod
    def clone(self, **kwargs):
        pass


class LeafModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, meta=None):
        AbsModel.__init__(self, name, meta)

    def fetch(self, rs):
        self.Requests.clear()
        self.Requests.add(rs)

    def exec(self):
        for req in self.Requests:
            self.do_request(req)
        self.drop_next()


class BranchModel(AbsModel, metaclass=ABCMeta):
    def __init__(self, name, meta=None):
        AbsModel.__init__(self, name, meta)
        self.Models = dict()

    @abstractmethod
    def select(self, mod):
        pass

    def fetch(self, res):
        self.Requests.clear()
        self.Requests.add(res)
        self.pass_down()

    def pass_down(self):
        res = self.Requests.pop_lower_requests()
        nest = dict()
        for req in res:
            m, req = req.down()
            try:
                nest[m].append(req)
            except KeyError:
                nest[m] = [req]

        for k, v in nest.items():
            self.select(k).fetch(v)

    def exec(self):
        for req in self.Requests:
            self.do_request(req)

        for v in self.Models.values():
            if v.tte == self.tte:
                v.exec()
        self.drop_next()

    @abstractmethod
    def do_request(self, req):
        pass
