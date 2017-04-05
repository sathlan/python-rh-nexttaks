class Review(object):
    """Wrapper around gerrit result object.

    """
    def __init__(self, gerrit, rtype, url):
        self.gerrit = gerrit
        self.rtype = rtype
        self.url = '{}#/c/{}/'.format(url, self.id)

    def __str__(self):
        topic = ''
        if 'topic' in self.gerrit:
            topic = self.gerrit['topic']
        return '#{0[_number]} {0[status]} - {0[owner][email]} - {0[subject]} - {0[branch]} {1}'.format(self.gerrit, topic)

    @property
    def branch(self):
        return self.gerrit['branch']

    @property
    def id(self):
        return self.gerrit['_number']

    @property
    def status(self):
        return self.gerrit['status']

    @property
    def workflow(self):
        workflow = {}
        if 'Workflow' in self.gerrit['labels']:
            workflow = self.gerrit['labels']['Workflow']
        return workflow

    @property
    def verified(self):
        verified = {}
        if 'Verified' in self.gerrit['labels']:
            verified = self.gerrit['labels']['Verified']
        return verified

    @property
    def code_review(self):
        code_review = {}
        if 'Code-Review' in self.gerrit['labels']:
            code_review = self.gerrit['labels']['Code-Review']
        return code_review

    def is_blocked_by_user_workflow(self):
        answer = False
        if 'blocking' in self.workflow:
            if 'rejected' in self.workflow and 'email' in self.workflow['rejected']:
                answer = True
        return answer

    def is_verified_disliked(self):
        return not self.is_abandoned() and 'disliked' in self.verified and 'username' in self.verified['disliked']

    def is_code_review_disliked(self):
        return not self.is_abandoned() and 'disliked' in self.code_review and 'username' in self.code_review['disliked']

    def is_code_user_verified(self):
        return self.verified and 'approved' in self.verified

    def is_disliked(self):
        return self.is_verified_disliked() or self.is_code_review_disliked()

    def is_abandoned(self):
        return 'ABANDONED' in self.gerrit['status']

    def is_merged(self):
        return 'MERGED' in self.gerrit['status']

    def need_review(self):
        return not self.is_abandoned() and not self.workflow \
            and not self.is_merged() \
            and not self.is_disliked() \
            and not self.is_code_user_verified()

    def need_merging(self):
        return not self.is_abandoned() \
            and not self.is_merged() and \
            ((self.workflow and not self.is_blocked_by_user_workflow() and not self.is_disliked())
             or
             (self.is_code_user_verified()))
