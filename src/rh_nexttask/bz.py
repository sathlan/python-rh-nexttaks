import logging
from pygerrit.rest import GerritRestAPI
from rh_nexttask.client import Client
from rh_nexttask.constants import Constants
from rh_nexttask.date import Date
from rh_nexttask.review import Review

logger = logging.getLogger('rh-nexttask')


class Bz(object):
    """Hold a reference to one bugzilla.

    """
    def __init__(self, bugzilla, dfg=None):
        self.bugzilla = bugzilla
        self.logger = logging.getLogger('rh-nexttask')

        # Seems it doesn't always work the first time for fixed_in.
        self._check_attributes()
        default_properties = {
            'id': None,
            'summary': bugzilla.summary.encode('utf-8'),
            'url': bugzilla.weburl,
            'status': None,
            'fixed_in': None,
            'id': None,
            'reviews': {},
            'external_bugs': None,
            'target_release': bugzilla.target_release[0],
            'keywords': None,
            'assigned_to': None,
            'internal_whiteboard': None,
            'devel_whiteboard': None,
            'target_milestone': None,
            'flags': None,
            'last_change_time': None,
            'version': None,
        }
        self.dfg = dfg
        self._upstream_gerrit = None
        self._internal_gerrit = None
        self._gerrit = {}
        self.upstream_reviews = []
        self.internal_reviews = []
        self.launchpad_ids = []
        self._planned_for = None
        self.is_client = False
        self.is_escalated = False
        self.advices = []
        self.clients = []
        self._pm_flags = None

        for (prop, default) in default_properties.items():
            if default:
                # When an true value we use it
                setattr(self, prop, default)
            else:
                # empty or false try to get it or set default
                setattr(self, prop, getattr(bugzilla, prop, default))

        self.no_change_during = Date(self.last_change_time).diff_date.days

        for ext in self.external_bugs:
            if 'type' in ext and 'description' in ext['type']:
                eid = ext['ext_bz_bug_id']
                eurl = ext['type']['url']
                etype = ext['type']['description']
                edescription = ext['type']['description']
                if edescription in 'OpenStack gerrit':
                    self.upstream_reviews.append(Review(self._get_review(eurl, eid), 'upstream', eurl))
                elif edescription in 'Red Hat Engineering Gerrit':
                    self.internal_reviews.append(Review(self._get_review(eurl, eid), 'internal', eurl))
                elif edescription in 'Launchpad':
                    self.launchpad_ids.append(eid)
                elif etype in 'Red Hat Customer Portal':
                    self.is_client = True
                    self.clients.append(Client(ext))
        if not self.is_client:
            # Check the whiteboard for any clue
            if 'client' in self.devel_whiteboard:
                self.is_client = True
                self.clients.append(Client({}))

        if 'escalated' in self.devel_whiteboard:
            self.is_escalated = True
            if not self.is_client:
                self.is_client = True
                self.clients.append(Client({}))

    def __str__(self):
        return '{} {} - {} - {}\t- {} - ({} days without activity)'.format(self.id,
                                                                           self.status,
                                                                           self.assigned_to,
                                                                           self.summary,
                                                                           self.planned_for,
                                                                           self.no_change_during)

    def _get_review(self, url, gerrit_id):
        request = "/changes/?q=change:{0}&o=LABELS&o=DETAILED_ACCOUNTS".format(gerrit_id)
        # python2/3 wonders
        # request = bytes(request.encode('utf-8'))
        request = self.gerrit(url).get(request)
        try:
            review = request[0]
        except IndexError:
            raise Exception("Cannot get review for {} on {} for BZ {}".format(gerrit_id, url, self.url))

        return review

    @property
    def planned_for(self):
        if self._planned_for is None:
            self._planned_for = 'Unknown'
            if self.target_milestone not in ['---']:
                self._planned_for = '{} {}'.format(self.version, self.target_milestone)
            elif self.target_release not in ['---']:
                self._planned_for = '{}'.format(self.target_release)
        return self._planned_for

    @property
    def pm_flags(self):
        if not self._pm_flags:
            self._pm_flags = [flag for flag in self.flags if flag['setter'] == 'pm-rhel@redhat.com']
        return self._pm_flags

    def gerrit(self, url):
        if url not in self._gerrit:
            ssl_verify = True
            if 'review.openstack.org' not in url:
                ssl_verify = False
            self._gerrit[url] = GerritRestAPI(url=url, auth=None, verify=ssl_verify)
        return self._gerrit[url]

    def _check_attributes(self):
        try:
            for attribute in Constants.INCLUDE_FIELDS:
                getattr(self.bugzilla, attribute)
        except AttributeError:
            self.logger.debug("Refreshing bug {}".format(self.bugzilla.id))
            self.bugzilla.refresh(Constants.INCLUDE_FIELDS)
