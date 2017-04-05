import logging
import bugzilla
import pickle
from rh_nexttask.bz import Bz
from rh_nexttask.constants import Constants

logger = logging.getLogger('rh-nexttask')


class BzCollector:
    def __init__(self, tokenfile, dfg=None, url=None):
        logger.debug('creating bzcollector')
        DEFAULT_URL = "https://bugzilla.redhat.com"

        self.url = url
        if not self.url:
            self.url = DEFAULT_URL
        self.tokenfile = tokenfile
        self.dfg = dfg
        self._bzapi = None
        self._bugs = []

    @classmethod
    def from_pickle(cls, path):
        logger.debug('creating bzcollector from pickle')
        bzc = cls(tokenfile=None)
        with open(path, 'rb') as f:
            bzc._bugs = pickle.load(f)
        return bzc

    def to_pickle(self, path):
        with open(path, 'wb') as f:
            # logger hold a file descriptor which doesn't pickle.
            old_log = self._bugs[0].logger
            for bug in self._bugs:
                bug.logger = None
            pickle.dump(self._bugs, f)
            for bug in self._bugs:
                bug.logger = old_log
#        pickle.dump(self._bugs, path)

    @property
    def bzapi(self):
        if not self._bzapi:
            self._bzapi = bugzilla.Bugzilla(url=self.url, tokenfile=self.tokenfile)
        return self._bzapi

    def bugs(self, request):
        bugs = self.bzapi.query(request)
        seen_id = []
        for bug in bugs:
            if bug.id not in seen_id:
                self._bugs.append(Bz(bug, self.dfg))
                seen_id.append(bug.id)
                # We don't recurse here, one level deep is good enough
                # unless proved otherwise.
                self._add_depends_on(bug, seen_id)

        return self._bugs

    def _add_depends_on(self, bug, seen_id):
        for dbug in bug.depends_on_all:
            if bug.id not in seen_id:
                self._bugs.append(Bz(self._bzapi.getbug(bug.id, Constants.INCLUDE_FIELDS), self.dfg))
                seen_id.append(bug.id)
