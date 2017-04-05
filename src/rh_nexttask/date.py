from datetime import datetime
from time import mktime


class Date(object):
    """Some time/date manipulation utilities.

    """
    def __init__(self, datetime):
        self.datetime = datetime
        self._diff_date = None

    @property
    def diff_date(self):
        if not self._diff_date:
            the_date = datetime.fromtimestamp(mktime(self.datetime.timetuple()))
            self._diff_date = datetime.now() - the_date
        return self._diff_date
