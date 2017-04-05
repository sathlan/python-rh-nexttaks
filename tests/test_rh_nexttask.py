import os
from click.testing import CliRunner

from rh_nexttask.cli import main

def filter_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/filter.ini')


def test_main():
    runner = CliRunner()
    filters = filter_path()
    result = runner.invoke(main, ['--queryfile', filters, '--query', 'exttesting'])

    assert result.exit_code == 0
