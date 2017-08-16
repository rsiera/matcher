import re

from django.conf import settings
from django.utils.text import force_unicode
from pysolr import Solr

ESCAPE_CHARS_RE = re.compile(r'(?<!\\)(?P<char>[&|+\-!(){}[\]^"~*?:])')


class SolrClient(object):

    def __init__(self):
        self.connection = Solr(settings.SOLR_CUSTOMER_SEARCH_URL)

    def carriers_by_name_and_city(self, name, city):
        query = self.get_query(name, city)
        results = self.connection.search(query, rows=5)
        return [{
            'id': r['Id'],
            'name': r['Name'],
            'city': r['City'],
            'agreements': self._get_agreements(r)
        } for r in results]

    def get_query(self, name, city):
        name_parts = force_unicode(name).split()
        city_parts = force_unicode(city).split()
        parts = [solr_escape(p) for p in (name_parts + city_parts)]
        query = u' OR '.join(u'"%s"' % p for p in parts)
        return u'(%s) AND (Type:"F")' % query

    def _get_agreements(self, r):
        return [{
                'name': k,
                'id': v,
                'Id': r['Id']
                } for k, v in r.iteritems() if k.startswith('agreement')]


def solr_escape(value):
    return ESCAPE_CHARS_RE.sub(r'\\\g<char>', value)
