from rh_nexttask.query import Query
from rh_nexttask.constants import Constants

def test_creation():
    a_bug = Query('section', [('attribute', 'value')])
    assert isinstance(a_bug, Query)

def test_make_query():
    q = Query('query1', [('param1', 'value1'),
                         ('description', 'My little query.'),
                         ('url', 'https://bugzilla.redhat.com/buglist.cgi?action=wrap&bug_status=NEW&bug_status=ASSIGNED&bug_status=POST&bug_status=MODIFIED&bug_status=ON_DEV&bug_status=ON_QA&bug_status=VERIFIED&classification=Red%20Hat&f1=component&f10=target_release&f2=OP&f3=cf_devel_whiteboard&f4=cf_internal_whiteboard&f5=CP&j2=OR&list_id=7549619&o1=notsubstring&o10=equals&o3=substring&o4=substring&product=Red%20Hat%20OpenStack&v1=doc&v10=10.0%20%28Newton%29&v3=DFG%3AUpgrade&v4=DFG%3AUpgrade'),
                         ('ignored', 'this is ignored')])
    query_hash = q.request()
    assert query_hash == {'action': 'wrap',
                          'bug_status': ['NEW',
                                         'ASSIGNED',
                                         'POST',
                                         'MODIFIED',
                                         'ON_DEV',
                                         'ON_QA',
                                         'VERIFIED'],
                          'classification': 'Red Hat',
                          'f1': 'component',
                          'f10': 'target_release',
                          'f2': 'OP',
                          'f3': 'cf_devel_whiteboard',
                          'f4': 'cf_internal_whiteboard',
                          'f5': 'CP',
                          'include_fields': Constants.INCLUDE_FIELDS,
                          'j2': 'OR',
                          'list_id': '7549619',
                          'o1': 'notsubstring',
                          'o10': 'equals',
                          'o3': 'substring',
                          'o4': 'substring',
                          'product': 'Red Hat OpenStack',
                          'v1': 'doc',
                          'v10': '10.0 (Newton)',
                          'v3': 'DFG:Upgrade',
                          'v4': 'DFG:Upgrade',}
