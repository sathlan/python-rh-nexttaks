from rh_nexttask.query import Query
from rh_nexttask.querycollector import QueryCollector

def test_creation():
    queries = QueryCollector()
    assert isinstance(queries, QueryCollector)

def test_from_file():
    queries = QueryCollector.from_file('/home/user/Src/sathlan/python-rh-nexttask/tests/fixtures/filter.ini')

    assert len(queries.queries_definition) == 4
    final_query = queries.select('testing')

    assert isinstance(final_query, Query)
#    assert final_query.request() == {}
