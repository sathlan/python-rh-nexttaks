from ConfigParser import RawConfigParser
from rh_nexttask.query import Query


class QueryCollector:

    def __init__(self):
        self.queries_definition = {}
        self.queries_file = None

    @classmethod
    def from_file(cls, queries_file):
        qs = cls()
        qs.queries_file = queries_file
        config = RawConfigParser()
        config.read(qs.queries_file)
        for query_name in config.sections():
            qs.queries_definition[query_name] = Query(
                query_name, config.items(query_name))
        return qs

    def select(self, name):
        if not self.queries_definition:
            self._parse_queries_from_file()
        if name in self.queries_definition:
            return self.queries_definition[name]
        else:
            return None

    def list(self):
        return [n for n in sorted(self.queries_definition.keys())]

    def list_str(self):
        header = 'Available queries in {}:'.format(self.queries_file)
        content = ''
        for query in self.list():
            content += "\t- {}\n".format(query)

        return "{}\n{}".format(header, content)
