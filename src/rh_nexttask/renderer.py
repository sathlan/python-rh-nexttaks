import logging

logger = logging.getLogger('rh-nexttask')


class Renderer(object):
    """Different way to render the advised bzs.

    """
    def __init__(self, bzs):
        self.bzs = bzs

    def list(self):
        raw_names = [f for f in dir(self) if f.startswith('r_')]
        return [f[2:] for f in raw_names]

    def list_str(self):
        header = 'Available renderers:'
        content = ''
        for renderer in self.list():
            content += "\t- {}\n".format(renderer)

        return "{}\n{}".format(header, content)

    @staticmethod
    def _display_bzs(bzs, sorting_key='no_change_during', url=False):
        for bz in sorted(bzs, reverse=True, key=lambda bz: getattr(bz, sorting_key)):
            header = "{} ({} since {} days):".format(bz, sorting_key, getattr(bz, sorting_key))
            content = ''
            if url:
                content = "\t\t{}\n".format(bz.url)
            for advice in bz.advices:
                content += "\t{}".format(advice)
            if not content:
                content = '\tCongratulation, state is OK.\n'
            print("{}\n{}".format(header, content))
        print("\nGot {} bzs.\n".format(len(bzs)))

    @staticmethod
    def _display_bzs_url_short(bzs, sorting_key='no_change_during'):
        for bz in sorted(bzs, reverse=True, key=lambda bz: getattr(bz, sorting_key)):
            print("{}\n\t{}".format(bz, bz.url))
        print("\nGot {} bzs.\n".format(len(bzs)))

    def r_echo(self):
        self._display_bzs(bzs=self.bzs, url=True)

    def r_echo_under_post(self):
        bzs_under_post = [bz for bz in self.bzs if bz.status in ['NEW', 'ASSIGNED', 'ON_DEV']]
        self._display_bzs(bzs=bzs_under_post, url=True)

    def _ask_for_review(self, title, rtype, show_bz=False):
        header = title
        content = ''
        for bz in sorted(self.bzs, reverse=True, key=lambda bz: bz.no_change_during):
            content_review = ''
            for advice in bz.advices:
                for review in advice.reviews:
                    if review and review.rtype == rtype:
                        logger.debug('Review {} has type {}'.format(review.id, review.rtype))
                        if advice.etype in ['need_merging', 'need_review']:
                            content_review += "  - {} - {}\n".format(review, advice.etype)
                            content_review += "      {}\n".format(review.url)
            if show_bz and content_review:
                content += '## BZ {} -- {}\n{}'.format(bz.id, bz.url, content_review)
            else:
                content += '{}'.format(content_review)

        if not content:
            content = 'Nothing need review.'
        print("{}\n{}\n".format(header, content))

    def r_tripleo_meeting(self):
        self._ask_for_review("Tripleo meeting", 'upstream')

    def r_daily_meeting(self):
        self._ask_for_review("Daily Meeting", 'internal', show_bz=True)

    def r_old_bug(self):
        na_bzs = [bz for bz in self.bzs if bz._need_action]
        bzs_users = {}
        for bz in na_bzs:
            if bz.assigned_to not in bzs_users:
                bzs_users[bz.assigned_to] = []
            bzs_users[bz.assigned_to].append(bz)
        for (user, bzs) in bzs_users.items():
            print "{}:\n".format(user)
            self._display_bzs(bzs, '_need_action_days')

    def r_bz_url(self):
        self._display_bzs_url_short(self.bzs)

    def r_bz_url_under_post(self):
        bzs_under_post = [bz for bz in self.bzs if bz.status in ['NEW', 'ASSIGNED', 'ON_DEV']]
        self._display_bzs_url_short(bzs_under_post)

    def r_client_bz(self):
        c_bzs = [bz for bz in self.bzs if bz.is_client]
        self._display_bzs_url_short(c_bzs)
