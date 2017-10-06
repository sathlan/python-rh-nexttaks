from rh_nexttask.advice import Advice
from rh_nexttask.constants import Constants
from rh_nexttask.date import Date


class Adviser(object):
    """Give advices on the next task around a bz.

    The bugzilla go through all the function named need_* to verify if
    the state is correct.

    Each advice is added to the bz in the bz.advices property list.

    To ease manipulation and check state of the current bz a
    bz._need_* property is created as well.  It's None by default, and
    set to True if an advice is given by the current function.

    Each need_* function can set its bz.need_* to True or False as
    well.  This enable other check function to verify some other
    state.  See the need_package/need_post function for an example.

    """
    def __init__(self, debug=None):
        self._debug = debug
        self._advices = []
        self._available_advices = []
        for afunc in self.available_advices:
            self._advices.append(getattr(self, afunc))

    def __str__(self):
        header = 'Available advices:'
        content = ''
        for advice in self.available_advices:
            content += "\t- {}\n".format(advice)
        return "{}\n{}".format(header, content)

    @property
    def available_advices(self):
        if not self._available_advices:
            self._available_advices = [f for f in dir(self) if f.startswith('need_')]
        return self._available_advices

    def need_triage(self, bz):
        if 'Triaged' not in bz.keywords:
            whiteboard = ''
            if bz.internal_whiteboard:
                whiteboard = ' from {} '.format(bz.internal_whiteboard)
            self._advice(bz, 'Bz {} should have the Triaged keywords.'.format(whiteboard))

    def need_code(self, bz):
        if not bz.upstream_reviews and not bz.internal_reviews and \
           not bz.fixed_in:
            self._advice(bz, 'Need to make some code')

    def need_release(self, bz):
        if bz.fixed_in and bz.status in ['VERIFIED']:
            self._advice(bz, '{} need release'.format(bz.fixed_in))

    def need_backport(self, bz):
        if bz.upstream_reviews and not bz.internal_reviews:
            reviews = bz.upstream_reviews
            for review in reviews:
                if review.status not in ['MERGED']:
                    continue
                if bz.target_release not in Constants.UPSTREAM_MAPPING:
                    # TODO: create a exception class
                    raise Exception("Cannot find {} as an upstream target"
                                    .format(bz.target_release))
                upstream_stable = Constants.UPSTREAM_MAPPING[bz.target_release]
                if not review.branch == upstream_stable:
                    self._advice(
                        bz,
                        'You need to backport the {} review {} to {}'
                        .format(review.rtype, review.id, upstream_stable),
                        review
                    )

    @staticmethod
    def _check_downstrean(bz, reviews_detail):
        merged = 0
        need_post = False
        for review in bz.internal_reviews:
            if review.status in ['MERGED']:
                merged += 1
                reviews_detail.append(review)
        if bz.internal_reviews and merged == len(bz.internal_reviews):
            need_post = True
        return need_post

    def need_post(self, bz):
        merged = 0
        need_post = False
        review_branch = []
        reviews = bz.upstream_reviews
        reviews_detail = []
        if bz.target_release not in Constants.UPSTREAM_MAPPING:
            # TODO: create a exception class
            raise Exception("Cannot find {} as an upstream target"
                            .format(bz.target_release))
        upstream_stable = Constants.UPSTREAM_MAPPING[bz.target_release]
        for review in reviews:
            if review.status in ['MERGED']:
                merged += 1
                reviews_detail.append(review)
                if review.branch not in review_branch:
                    review_branch.append(review.branch)

        if merged == len(reviews):
            if upstream_stable in Constants.DOWNSTREAM_ONLY:
                need_post = self._check_downstrean(bz, reviews_detail)
            else:
                # If not the same branches then some more work is needed.
                if len(review_branch) == 1:
                    if review_branch[0] == upstream_stable:
                        if upstream_stable == 'master':
                            need_post = True
                        else:
                            need_post = self._check_downstrean(bz, reviews_detail)
        if need_post:
            if bz.status in ['NEW', 'ASSIGNED', 'ON_DEV']:
                self._advice(
                    bz,
                    'You need to change the bz to POST',
                    reviews_detail
                )

    def need_merging(self, bz):
        reviews = bz.upstream_reviews + bz.internal_reviews
        for review in reviews:
            if review.need_merging():
                self._advice(
                    bz,
                    '{} review {} could be merged'.format(review.rtype, review.id),
                    review
                )

    def need_review(self, bz):
        reviews = bz.upstream_reviews + bz.internal_reviews
        for review in reviews:
            if review.need_review():
                self._advice(
                    bz,
                    '{} review {} needs review'.format(review.rtype, review.id),
                    review
                )

    def need_downstream(self, bz):
        if bz.upstream_reviews and not bz.internal_reviews:
            merged = 0
            reviews = bz.upstream_reviews
            for review in reviews:
                if review.status in ['MERGED']:
                    merged += 1
            if merged == len(reviews):
                if not bz.internal_reviews and \
                   Constants.UPSTREAM_MAPPING[bz.target_release] != 'master':
                    self._advice(
                        bz,
                        '{} review {} needs an internal backport'.format(review.rtype, review.id),
                        review
                    )

    def need_user_workflow(self, bz):
        reviews = bz.upstream_reviews + bz.internal_reviews
        for review in reviews:
            if review.is_blocked_by_user_workflow():
                user = ''
                if 'email' in review.workflow['rejected']:
                    user = ' by {}'.format(review.workflow['rejected']['email'])
                self._advice(
                    bz,
                    '{} review {} is workflow-1{}'.format(review.rtype, review.id, user),
                    review
                )

    def need_checking_verification(self, bz):
        reviews = bz.upstream_reviews + bz.internal_reviews
        for review in reviews:
            if review.is_verified_disliked():
                user = review.verified['disliked']['username']
                self._advice(
                    bz,
                    '{} review {} failed verification by {}, need to check why.'.format(review.rtype, review.id, user),
                    review
                )

    def need_checking_review(self, bz):
        reviews = bz.upstream_reviews + bz.internal_reviews
        for review in reviews:
            if review.is_code_review_disliked():
                user = review.code_review['disliked']['username']
                self._advice(
                    bz,
                    '{} review {} is disliked by {}, need to check why.'.format(review.rtype, review.id, user),
                    review
                )

    def need_package(self, bz):
        reviews = bz.upstream_reviews + bz.internal_reviews
        if not reviews:
            return None
        # Dependency handling.
        if bz._need_post is None:
            self.need_post(bz)
        if bz._need_downstream is None:
            self.need_downstream
        if bz._need_checking_verification is None:
            bz.need_checking_verification(bz)
        if bz._need_checking_review is None:
            bz.need_checking_review(bz)
        if not bz._need_post and not bz._need_downstream \
           and not bz._need_checking_verification \
           and not bz._need_merging \
           and not bz._need_checking_review:
            need_review = False
            is_abandoned = False
            abandoned = 0
            for review in reviews:
                if review.need_review():
                    need_review = True
                if review.is_abandoned():
                    abandoned += 1
            if abandoned == len(reviews):
                is_abandoned = True
            if not bz.fixed_in and not need_review and not is_abandoned:
                self._advice(bz, 'Code from those reviews should be packaged', reviews)

    def need_verified(self, bz):
        if bz.status in ['MODIFIED', 'ON_QA']:
            pkg = bz.fixed_in
            if not pkg:
                pkg = '*MISSING PACKAGE*'
            self._advice(bz, 'Bz package {} need to be moved to VERIFIED'.format(pkg))

    def need_modified(self, bz):
        if bz.fixed_in and bz.status not in ['MODIFIED', 'ON_QA', 'VERIFIED']:
            self._advice(bz, 'Bz needs to move to MODIFIED or ON_QA')

    def need_target_version(self, bz):
        if bz.planned_for in ['Unknown']:
            self._advice(bz, "Bz should have a target release or a target milestone set, "
                         "maybe using the ZStream or FutureFeature keywords.")

    def need_client_attention(self, bz):
        if bz.is_client:
            self._advice(bz, "This is a client bug, make sure to treat it with attention.")

    def need_escalated_attention(self, bz):
        if bz.is_escalated:
            self._advice(bz, "This is an escalated bug, make sure to treat it with speed.")

    def need_blocker_pm_ack(self, bz):
        for flag in bz.flags:
            if 'blocker' in flag['name']:
                if flag['status'] == '?':
                    blocker_date = flag['creation_date']
                    ndays = Date(blocker_date).diff_date.days
                    self._advice(bz, "{} wants pm to ack the blocker flag for {} days"
                                 .format(flag['setter'], ndays), None, ndays)

    def need_blocker_attention(self, bz):
        for flag in bz.flags:
            if 'blocker' in flag['name']:
                if flag['status'] in ['+', '-', '?']:
                    self._advice(bz, "Blocker bug, please fix it asap")

    def need_info(self, bz):
        for flag in bz.flags:
            if 'needinfo' in flag['name']:
                requestee = ''
                if 'requestee' in flag:
                    requestee = flag['requestee']
                diff = Date(flag['modification_date']).diff_date
                self._advice(bz, "{} need information from {} since {} days.".format(flag['setter'],
                                                                                     requestee,
                                                                                     diff.days))

    def need_action(self, bz):
        last_change = bz.last_change_time
        ndays = Date(last_change).diff_date.days
        if ndays >= 30:
            self._advice(bz, "Bz hasn't seen any activity form more than 30 days ({})."
                         .format(ndays), None, ndays)

    def need_rfe_dev(self, bz):
        if 'FutureFeature' in bz.keywords:
            self._advice(bz, "Bz is an RFE for {}, make sure to code in time."
                         .format(Constants.UPSTREAM_MAPPING[bz.target_release]))

    def need_zstream_dev(self, bz):
        if 'ZStream' in bz.keywords:
            self._advice(bz, "Bz is an Zstream for {}, make sure to code in time."
                         .format(Constants.UPSTREAM_MAPPING[bz.target_release]))

    def need_zstream_pm_ack(self, bz):
        if 'ZStream' in bz.keywords and bz.pm_flags:
            zstream = Constants.ZSTREAM_MAPPING[bz.target_release]
            zflags = [flag for flag in bz.pm_flags if flag['name'] == zstream]
            if zflags:
                has_ack = zflags[0]['status'] == '+'
                if not has_ack:
                    self._advice(bz, "Bz need zstream approval from PM for {}."
                                 .format(Constants.ZSTREAM_MAPPING[bz.target_release]))

    def need_other_dfg_attention(self, bz):
        if getattr(bz, 'dfg', False):
            if bz.dfg != bz.internal_whiteboard:
                self._advice(bz, "Bz need attention from another dfg: {}".format(bz.internal_whiteboard))

    def _advice(self, bz, message, reviews=None, ndays=None):
        advice = Advice(message=message, reviews=reviews, ndays=ndays)
        bz.advices.append(advice)
        if advice.etype:
            setattr(bz, '_{}'.format(advice.etype), True)
        if ndays:
            setattr(bz, '_{}_days'.format(advice.etype), ndays)

    def advice(self, bz):
        if self._debug:
            if bz.id == self._debug:
                reviews = bz.upstream_reviews + bz.internal_reviews
                review = 'None'
                if reviews:
                    review = reviews[0]
                print('{}'.format(review))
                import pdb
                pdb.set_trace()
        # Ensure every bz has a tip property defined to None.
        for tip in self.available_advices:
            setattr(bz, '_{}'.format(tip), None)
            setattr(bz, '_{}_days'.format(tip), -1)

        for tip in self._advices:
            # If property has already been run return it.
            prop = '_{}'.format(tip.__name__)
            attr = getattr(bz, prop)
            if attr is not None:
                return attr
            # Set it to False by default
            setattr(bz, prop, False)
            # Run it.
            tip(bz)

        if bz.id == self._debug:
            reviews = bz.upstream_reviews + bz.internal_reviews
            review = 'None'
            if reviews:
                review = reviews[0]
            print('{}'.format(review))
            import pdb
            pdb.set_trace()
