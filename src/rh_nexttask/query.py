from bugzilla import Bugzilla
from rh_nexttask.constants import Constants


class Query:
    def __init__(self, name, configuration):
        self.name = name
        self.reserved_keywords = ['documentation', 'url', 'extra', 'dfg']
        self._request = None
        self.bz_query_url = None
        for prop in self.reserved_keywords:
            setattr(self, prop, None)

        for (prop, value) in configuration:
            if prop in self.reserved_keywords:
                if prop is 'url':
                    self._check_url(prop)
                setattr(self, prop, value)

    def __str__(self):
        return '{}'.format(self._request)

    def request(self, extra_fields={}):
        if not self._request:
            self._request = Bugzilla(url=None).url_to_query(self.url)
            self._request.update(extra_fields)
            self._request.update({
                'include_fields': Constants.INCLUDE_FIELDS,
            })
        return self._request

    @classmethod
    def from_bz(cls, bz, documentation="Search specific bzs"):
        # https://bugzilla.redhat.com/report.cgi?x_axis_field=target_release&y_axis_field=bug_status&z_axis_field=&no_redirect=1&query_format=report-table&short_desc_type=allwordssubstr&short_desc=&classification=Red+Hat&product=Red+Hat+OpenStack&bug_status=NEW&bug_status=ASSIGNED&bug_status=POST&bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&bug_status=VERIFIED&bug_status=RELEASE_PENDING&bug_status=CLOSED&longdesc_type=allwordssubstr&longdesc=&bug_file_loc_type=allwordssubstr&bug_file_loc=&status_whiteboard_type=allwordssubstr&status_whiteboard=&keywords_type=allwords&keywords=&deadlinefrom=&deadlineto=&bug_id=&bug_id_type=anyexact&votes=&votes_type=greaterthaneq&emailtype1=substring&email1=&emailtype2=substring&email2=&emailtype3=substring&email3=&chfieldvalue=&chfieldfrom=&chfieldto=Now&j_top=OR&f1=bug_id&o1=equals&v1=1451275&f2=bug_id&o2=equals&v2=1461531&f3=bug_id&o3=equals&v3=1472340&f4=bug_id&o4=equals&v4=1472343&f5=bug_id&o5=equals&v5=1472347&format=table&action=wrap
        # https://bugzilla.redhat.com/buglist.cgi?action=wrap&bug_status=NEW&bug_status=ASSIGNED&bug_status=POST&bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&bug_status=VERIFIED&bug_status=RELEASE_PENDING&bug_status=CLOSED&classification=Red%20Hat&f1=OP&f2=bug_id&f3=bug_id&f4=bug_id&f5=bug_id&f6=bug_id&f7=CP&j1=OR&list_id=7602378&o2=equals&o3=equals&o4=equals&o5=equals&o6=equals&product=Red%20Hat%20OpenStack&v2=1451275&v3=1461531&v4=1472340&v5=1472343&v6=1472347
        bzs = []
        if type(bz) is not list and type(bz) is not tuple:
            bzs = list([bz])
        else:
            bzs = list(bz)

        query_str = 'https://bugzilla.redhat.com/buglist.cgi?action=wrap&bug_status=NEW&bug_status=ASSIGNED&bug_status=POST&bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&bug_status=VERIFIED&bug_status=RELEASE_PENDING&bug_status=CLOSED&f1=OP&f7=CP&j1=OR'
        cpt = 2
        for bbz in bzs:
            query_str += "&f{0}=bug_id&o{0}=equals&v{0}={1}".format(cpt, bbz)
            cpt += 1

        query = cls('id', [('url', query_str),
                           ('documentation', documentation)])
        setattr(query, 'bz_query_url', query_str)
        return query

    @staticmethod
    def _check_url(url):
        if not url.find('/buglist.cgi'):
            # TODO: make a class for exception.
            raise Exception("You must pass a buglist.cgi request, not {}".format(url))
