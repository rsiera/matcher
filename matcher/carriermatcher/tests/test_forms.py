import mock
import os

from django.contrib.auth import get_user_model
from django.core.files import File
from django.test import TestCase

from ..forms import MatchingRequestForm, MatchCompanyForm


class MatchingRequestFormTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_non_valid_input_data(self):
        form = MatchingRequestForm(user=1, data={})
        form.is_valid()
        self.assertIn('uploaded', form.errors)

    def test_valid_input_data(self):
        user = get_user_model().objects.create_user('test', email='e@example.com', password='test')
        uploaded = os.path.join(os.path.dirname(__file__), 'carrierlist_ok.xls')

        with open(uploaded) as f:
            form = MatchingRequestForm(user=user, files={'uploaded': File(f)})
            self.assertEqual(0, len(form.errors), form.errors)
            self.assertTrue(form.is_valid())

    def test_only_uploaded_field_in_form(self):
        form = MatchingRequestForm(user=1)
        self.assertIn('uploaded', form.fields)
        self.assertEqual(1, len(form.fields))


class MatchCompanyFormTest(TestCase):

    def test_name_and_city_are_required(self):
        form = MatchCompanyForm({})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('city', form.errors)

    @mock.patch('matcher.carriermatcher.forms.SolrClient')
    def test_match_runs_solr_search(self, SolrClient):
        SolrClient().carriers_by_name_and_city.return_value = [{'id': 123456}]
        form = MatchCompanyForm({'name': "a", 'city': "b"})
        form.is_valid()
        companies = form.match()
        assert SolrClient().carriers_by_name_and_city.called
        self.assertEqual(companies, [{'id': 123456}])
