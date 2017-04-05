"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mrh_nexttask` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``rh_nexttask.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``rh_nexttask.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import click
import logging
import os
import sys
from rh_nexttask.query import Query
from rh_nexttask.querycollector import QueryCollector
from rh_nexttask.bzcollector import BzCollector
from rh_nexttask.adviser import Adviser
from rh_nexttask.renderer import Renderer

logging.basicConfig()
logger = logging.getLogger('rh-nexttask')


@click.command()
@click.option('--query',
              help='Which query to use. Use "list" to get the in the filter file')
@click.option('--queryfile',
              help='Filter definition file to use.',
              type=click.Path(exists=True))
@click.option('--tokenfile',
              help='Tokenfile to use, default to ~/.bugzillatoken',
              type=click.Path(exists=True),
              default=os.path.expanduser('~/.bugzillatoken'))
@click.option('--render',
              multiple=True,
              default=['echo'],
              help='Renderer to use, can be repeated.  Default to echo.  Use "list" to get their names.')
@click.option('--show',
              multiple=True,
              default=[],
              help='Show only those states. Can be repeated.  Default to None.  Use "list" to get their names.  Can be inverted by prefixing with "no-"')
@click.option('--user',
              default=None,
              help='Show only the bz belonging to that user email.')
@click.option('--debug',
              default=None,
              type=int,
              help='Developer option.  Enable debug console on the specified bz id.')
@click.option('--bz-id',
              default=[],
              type=int,
              multiple=True,
              help='Get advice on this bug.  Will take precedence on other query options.')
@click.option('--dump',
              default=None,
              help='dump all the bz (pickle) in a file for later re-use with --restore ')
@click.option('--restore',
              default=None,
              type=click.Path(exists=True),
              help='dump all the bz (pickle) in a file for later re-use with --restore ')
@click.option('--log-level',
              default=None,
              help='Log level to use: debug, info')
@click.option('--dump-query',
              default=None,
              help="Dump the metric. Give a tag (no space txt) as argument.")
def main(query, queryfile, tokenfile, render, show, user, debug, bz_id, dump, restore, log_level, dump_query):
    if log_level:
        if log_level == 'debug':
            logger.setLevel(logging.DEBUG)
        elif log_level == 'info':
            logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.CRITICAL)
    adviser = Adviser(debug)

    if 'list' in show:
        click.echo(adviser)
        sys.exit()

    for advice in show:
        real_name_advice = advice
        if advice.find('no-') == 0:
            real_name_advice = advice[3:]
        if real_name_advice not in adviser.available_advices:
            raise click.UsageError("Advice \"{}\" is not available.\n{}".format(advice,
                                                                                adviser))
    if 'list' in render:
        click.echo(Renderer(None).list_str())
        sys.exit()

    renderer_list = Renderer(None).list()
    for display in render:
        if display not in renderer_list:
            raise click.UsageError("Render \"{}\" is not available.\n{}".format(display,
                                                                                Renderer(None).list_str()))

    if dump_query:
        if bz_id:
            query = Query.from_bz(bz_id)
            click.echo("[{}]\nurl = {}\ndocumentation = \nextra = {}".format(dump_query,
                                                                             query.bz_query_url,
                                                                             ','.join([str(bz) for bz in bz_id])))
            sys.exit()
        else:
            raise click.UsageError("dump-query work only with --bz-id option.")

    if restore:
        bzc = BzCollector.from_pickle(restore)
        bzs = bzc._bugs
        if bz_id:
            bzs = [bz for bz in bzs if bz.id in bz_id]
        if user:
            bzs = [bz for bz in bzs if bz.assigned_to == user]
    elif bz_id:
        query = Query.from_bz(bz_id)
        q_json = query.request()
        bzc = BzCollector(tokenfile)
        bzs = bzc.bugs(q_json)
    else:
        if not queryfile:
            raise click.UsageError("You must give a filter file.")
        queryfile = os.path.abspath(queryfile)
        if not query:
            raise click.UsageError("You must give a query to choose from queryfile.")
        if query == 'list':
            click.echo(QueryCollector.from_file(queryfile).list_str())
            sys.exit()
        if query not in QueryCollector.from_file(queryfile).list():
            raise click.UsageError("Query \"{}\" is not available.\n{}".format(query,
                                                                               QueryCollector.from_file(queryfile).list_str()))

        qcollector = QueryCollector.from_file(queryfile)
        extra_fields = {}
        if user:
            extra_fields.update({'assigned_to': user})
        query = qcollector.select(query)
        q_json = query.request(extra_fields)
        if not q_json:
            click.error('{} is not part of {}'.format(q_json, queryfile))
        bzc = BzCollector(tokenfile, query.dfg)
        bzs = bzc.bugs(q_json)

    if dump:
        bzc.to_pickle(dump)

    for bz in bzs:
        adviser.advice(bz)
    selected_bz = []
    filter_removal = []
    for f in show:
        real_name_advice = f
        if f.find('no-') == 0:
            filter_removal += [f[3:]]
        else:
            selected_bz += [b for b in bzs if getattr(b, '_{}'.format(f), False)]
    if not selected_bz and not show:
        selected_bz = bzs
    for f in filter_removal:
        selected_bz = [b for b in selected_bz if not getattr(b, '_{}'.format(f), False)]

    renderer = Renderer(selected_bz)
    for display in render:
        if len(render) > 1:
            click.echo("{} ======".format(display))
        getattr(renderer, 'r_{}'.format(display))()
