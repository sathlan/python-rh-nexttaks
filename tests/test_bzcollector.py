import os
from rh_nexttask.bzcollector import BzCollector
from rh_nexttask.constants import Constants
from bugzilla.bug import Bug
from bugzilla import Bugzilla

def test_creation():
    bz_handler = BzCollector('/token.file', 'http://bug.api.url')
    assert isinstance(bz_handler, BzCollector)

def __bug(bz_handler):
    data = {
        "bug_id": 123456,
        "external_bugs": [],
        "keywords": "vkeyword",
        "assigned_to": "vassigned_to",
        "depends_on_all": [],
        "fixed_in": "",
        "status": "NEW",
        "assigned_to": "foo@bar.com",
        "component": "foo",
        "product": "bar",
        "short_desc": "some short desc",
        "cf_fixed_in": "nope",
        "fixed_in": "1.2.3.4",
        "devel_whiteboard": "some status value",
        "target_release": "---",
        }

    return [Bug(bugzilla=bz_handler, dict=data)]

