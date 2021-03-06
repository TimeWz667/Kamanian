from abc import ABCMeta, abstractmethod
from complexism.mcore import ModelAtom
from complexism.element import AbsTicker, Event

__author__ = 'TimeWz667'
__all__ = ['AbsActor', 'PassiveActor', 'ActiveActor']


class AbsActor(ModelAtom, metaclass=ABCMeta):
    def __init__(self, name, pars=None):
        ModelAtom.__init__(self, name, pars=pars)

    @abstractmethod
    def register(self, sub_model, ti):
        pass

    def fill(self, obs: dict, model, ti):
        pass

    @staticmethod
    @abstractmethod
    def decorate(name, model, **kwargs):
        pass

    @abstractmethod
    def match(self, be_src, ags_src, ags_new, ti):
        pass


class ActiveActor(AbsActor, metaclass=ABCMeta):
    def __init__(self, name, clock: AbsTicker, pars=None):
        AbsActor.__init__(self, name, pars=pars)
        self.Clock = clock

    def find_next(self):
        return self.compose_event(self.Clock.Next)

    def execute_event(self):
        """
        Do not use
        """
        pass

    def operate(self, model):
        event = self.Next
        time = event.Time
        self.Clock.update(time)
        self.do_action(model, event.Todo, time)
        self.drop_next()

    def initialise(self, ti, *args, **kwargs):
        self.Clock.initialise(ti)

    def reset(self, ti, *args, **kwargs):
        self.Clock.initialise(ti)

    @abstractmethod
    def compose_event(self, ti):
        """
        Compose the next event
        :param ti: current time
        :return:
        :rtype:
        """
        pass

    @abstractmethod
    def do_action(self, model, td, ti):
        """
        Let an event occur
        :param model: source model
        :param td: action to be done
        :param ti: time
        :type: double
        :return:
        """
        pass


class PassiveActor(AbsActor, metaclass=ABCMeta):
    def __init__(self, name, pars=None):
        AbsActor.__init__(self, name, pars=pars)

    @property
    def Next(self):
        return Event.NullEvent

    @property
    def TTE(self):
        return float('inf')

    def drop_next(self):
        return

    def find_next(self):
        pass

    def execute_event(self):
        pass
