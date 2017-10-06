class Constants:
    INCLUDE_FIELDS = [
        'external_bugs',
        'id',
        'summary',
        'assigned_to',
        'status',
        'keywords',
        'depends_on_all',
        'fixed_in',
        'devel_whiteboard',
        'internal_whiteboard',
        'devel_whiteboard',
        'target_release',
        'target_milestone',
        'flags',
        'last_change_time',
        'assigned_to',
        'version',
    ]

    URL = "bugzilla.redhat.com"
    COOL_DOCS = ['https://mojo.redhat.com/docs/DOC-1100291#jive_content_id_Method_being_used']
    UPSTREAM_MAPPING = {
        '6.0 (Juno)': 'stable/juno',
        '7.0 (Kilo)': 'stable/kilo',
        '8.0 (Liberty)': 'stable/liberty',
        '9.0 (Mitaka)': 'stable/mitaka',
        '10.0 (Newton)': 'stable/newton',
        '11.0 (Ocata)': 'stable/ocata',
        '12.0 (Pike)': 'stable/pike',
        '13.0 (Queens)': 'master',
        '---': 'master',
    }
    ZSTREAM_MAPPING = {
        '6.0 (Juno)': 'rhos-6.0.z',
        '7.0 (Kilo)': 'rhos-7.0.z',
        '8.0 (Liberty)': 'rhos-8.0.z',
        '9.0 (Mitaka)': 'rhos-9.0.z',
        '10.0 (Newton)': 'rhos-10.0.z',
        '11.0 (Ocata)': 'rhos-11.0.z',
        '12.0 (Pike)': 'stable/pike',
        '13.0 (Queens)': 'master',
        '---': 'master',
    }

    DOWNSTREAM_ONLY = ['stable/juno', 'stable/kilo', 'stable/liberty', 'stable/mitaka']
