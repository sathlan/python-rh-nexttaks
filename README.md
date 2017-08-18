# Overview

This glue together upstream/downstream review and bugzilla status.

It gives advices on the bugzilla state after having collected the
state of upstream and downstream review.

It can dumps the current state in a pickle file to be able to query
different status quickly.

All command should be self explanatory:

    rh-nexttask --help
    Usage: rh-nexttask [OPTIONS]

    Options:
      --query TEXT       Which query to use. Use "list" to get the in the filter
                         file
      --queryfile PATH   Filter definition file to use.
      --tokenfile PATH   Tokenfile to use, default to ~/.bugzillatoken
      --render TEXT      Renderer to use, can be repeated.  Default to echo.  Use
                         "list" to get their names.
      --show TEXT        Show only those states. Can be repeated.  Default to
                         None.  Use "list" to get their names.  Can be inverted by
                         prefixing with "no-"
      --user TEXT        Show only the bz belonging to that user email.
      --debug INTEGER    Developer option.  Enable debug console on the specified
                         bz id.
      --bz-id INTEGER    Get advice on this bug.  Will take precedence on other
                         query options.
      --dump TEXT        dump all the bz (pickle) in a file for later re-use with
                         --restore
      --restore PATH     dump all the bz (pickle) in a file for later re-use with
                         --restore
      --log-level TEXT   Log level to use: debug, info
      --dump-query TEXT  Dump the metric. Give a tag (no space txt) as argument.
      --help             Show this message and exit.

The render and show create the list of available option when you use
the "list" options.

You need a valid bugzilla token file.  You can easily get one using

    bugzilla login

from the python-bugzilla package.

# Example

Get the state of all bugzillas and save it in a pickle file.

    rh-nexttask --query all-upgrade --queryfile ~/Src/python-rh-nexttask/data/filter.ini_sample --dump /tmp/all-upgrade.data > /tmp/all-bugs.txt

See the data/filter.ini_sample to see what the --query parameter matches.

Get all the bz that need to be move to post using the previously generate pickle file.

    rh-nexttask --restore /tmp/all-upgrade.data --show need_post

Get all current blocker bug list which are under POST:

    rh-nexttask --restore /tmp/all-upgrade.data --show need_blocker_attention --show no-need_other_dfg_attention  --render echo_under_post

Get all untriaged bug:

    rh-nexttask --restore /tmp/all-upgrade.data --show need_triage --show no-need_other_dfg_attention

Get the list of upstream code that needs review associted with blocker bugs

    rh-nexttask --restore /tmp/all-upgrade.data --show need_blocker_attention --show no-need_other_dfg_attention  --render tripleo_meeting

Get the list of downstream review that need review:

    rh-nexttask --restore /tmp/all-upgrade.data   --render daily_meeting

Get the list of bz that have all code merged and must be moved to POST:

    rh-nexttask --restore /tmp/all-upgrade.data --show need_post

And many (too much) more, look at the

    rh-nexttask --show list
    rh-nexttask --render list

# Shortcoming.

Currently you can't logically and the "--show" filter.
