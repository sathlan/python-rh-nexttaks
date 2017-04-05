from rh_nexttask.adviser import Adviser

def test_adviser():
    a_adviser = Adviser()
    assert isinstance(a_adviser, Adviser)
