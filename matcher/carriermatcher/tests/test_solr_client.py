import mock
from django.test import TestCase

from ..solr_client import SolrClient, solr_escape


class SolrClientTest(TestCase):

    def test_get_query(self):
        client = SolrClient()
        query = client.get_query('Test Company', 'Nowe Brzesko')
        expected = (
            '("Test" OR "Company" OR "Nowe" OR "Brzesko") '
            'AND (Type:"F")'
        )
        self.assertEqual(query, expected)

    def test_solr_escape(self):
        tests = [
            ('', ''),
            ('a', 'a'),
            ('"stuff"', '\\"stuff\\"'),
            ('!this', '\\!this'),
        ]
        for value, output in tests:
            self.assertEqual(solr_escape(value), output)

    def test_carrier_by_name_and_city(self):
        client = SolrClient()
        client.connection = mock.Mock()
        client.connection.search.return_value = SAMPLE_RESULTS
        result = client.carriers_by_name_and_city('Company', 'City')
        self.assertEqual(len(SAMPLE_RESULTS), len(result))

        r = result[0]
        self.assertEqual(SAMPLE_RESULTS[0]['Name'], r['name'])
        self.assertEqual(SAMPLE_RESULTS[0]['City'], r['city'])
        self.assertEqual(SAMPLE_RESULTS[0]['Id'], r['id'])

        agreements = r['agreements']
        self.assertEqual(3, len(agreements))

        expected_result = sorted([
            {
                'name': 'agreementAlfa',
                'id': 'Version 2013-04-15',
                'Id': 1
            }, {
                'name': 'agreementBeta',
                'id': 'Version 2013-04-16',
                'Id': 1
            }, {
                'name': 'agreementDelta',
                'id': 'Version 2013-04-17',
                'Id': 1
            },
        ], key=lambda k: k['name'])

        self.assertListEqual(
            expected_result, sorted(agreements, key=lambda k: k['name']))


SAMPLE_RESULTS = [
    {
        u'Id': 1,
        u'Name': u'Company #1',
        u'City': u'Krakow',
        u'Type': u'F',
        u'agreementAlfa': u'Version 2013-04-15',
        u'agreementBeta': u'Version 2013-04-16',
        u'agreementDelta': u'Version 2013-04-17',
    },
    {
        u'Id': 2,
        u'Name': u'Company #2',
        u'City': u'Krakow',
        u'Type': u'F',
        u'agreementBeta': u'Version 2011-03-30 3.5',
    },
    {
        u'Id': 3,
        u'Name': u'Company #3',
        u'City': u'Krakow',
        u'Type': u'F',
        u'agreementAlfa': u'Version 2011-07-01 4.1',
    },
    {
        u'Id': 4,
        u'Name': u'Company #4',
        u'City': u'Krakow',
        u'Type': u'F',
        u'agreementAlfa': u'No agreement',
    },
    {
        u'Id': 5,
        u'Name': u'Company #5',
        u'Type': u'F',
        u'City': u'Krakow',
        u'agreementAlfa': u'No agreement',
    },
]
