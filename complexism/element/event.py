__author__ = 'TimeWz667'
__all__ = ['Event']


class Event:
    NullEvent = None

    def __init__(self, td, ti, msg=None):
        """
        To do something at a certain time
        :param td: a thing to do
        :param ti: a certain time for the event
        :param msg: message to report
        """
        self.Time = ti
        self.Todo = td
        self.__message = msg if msg else str(td)

    def __call__(self, *args, **kwargs):
        return self.Todo

    def __gt__(self, ot):
        return self.Time > ot.Time

    def __le__(self, ot):
        return self.Time <= ot.Time

    def __eq__(self, ot):
        return self.Time == ot.Time

    def cancel(self):
        self.Todo = None

    def is_cancelled(self):
        return self.Todo is None

    @property
    def Message(self):
        return self.__message

    def __repr__(self):
        return 'Event({} at {})'.format(self.Message, self.Time)

    def __str__(self):
        return '{}: {}'.format(self.Todo, self.Time)


Event.NullEvent = Event(None, float('inf'))
