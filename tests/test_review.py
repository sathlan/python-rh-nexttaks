from rh_nexttask.review import Review

def test_review():
    gerrit_obj = {
        'branch': 'master',
        '_number': '1',
        'status': 'NEW',
        'labels': {}
    }
    a_review = Review(gerrit_obj, 'upstream', 'http://review')
    assert isinstance(a_review, Review)
