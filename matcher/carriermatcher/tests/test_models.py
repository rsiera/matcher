import os
from django.test import TestCase

from ..excel_models import CarrierExcel


class CarrierExcelTest(TestCase):

    def test_false_if_not_properly_file(self):
        path = os.path.join(os.path.dirname(__file__), 'carrierlist_wrong.xls')
        with open(path) as f:
            excel = CarrierExcel(f.read())

        self.assertFalse(excel.is_valid())

    def test_read_ok_file(self):
        path = os.path.join(os.path.dirname(__file__), 'carrierlist_ok.xls')
        with open(path) as f:
            excel = CarrierExcel(f.read())

        self.assertTrue(excel.is_valid())
