import inspect


class Advice(object):
    """Hold an advice for a bugzilla workflow.

    """
    def __init__(self, message, reviews=None, ndays=None):
        self.message = message
        self.reviews = reviews
        if not isinstance(self.reviews, list) and reviews:
            self.reviews = [reviews]
        elif reviews is None:
            self.reviews = []
        try:
            # Must be called from the Adviser._advice wrapper for this
            # to work. 2 is the stack parenthood and 3 is the function
            # name.
            self.etype = inspect.stack()[2][3]
        except IndexError:
            self.etype = 'Unknown'

    def __str__(self):
        header = '{}: {}'.format(self.etype, self.message)
        content = ''
        for review in self.reviews:
            content += "\t- {}\n".format(review)
            content += "\t\t{}\n".format(review.url)
        return "{}\n{}".format(header, content)
