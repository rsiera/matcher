import xlrd
from StringIO import StringIO
from xlutils.copy import copy as copy_workbook


class CarrierData(object):

    def __init__(self, row_number, name, city, street, country, company_id, agreement_versions):
        self.row_number = row_number
        self.name = name
        self.city = city
        self.country = country
        self.street = street
        self.name = name
        self.company_id = company_id
        self.agreement_versions = agreement_versions

    @property
    def company_id_int(self):
        try:
            return int(self.company_id)
        except ValueError:
            return None

    def attrs(self):
        return {
            'row_number': self.row_number,
            'name': self.name,
            'city': self.city,
            'street': self.street,
            'country': self.country,
            'company_id': self.company_id_int,
            'agreement_versions': self.agreement_versions,
        }


class CarrierExcel(object):
    company_id_column = 1
    name_column = 5
    street_column = 12
    city_column = 14
    country_column = 15
    agreements_column = 21

    def __init__(self, file_contents):
        self.file_contents = file_contents
        self.workbook = xlrd.open_workbook(
            file_contents=file_contents, formatting_info=True)
        self.data = list(self.get_carrier_data(self.workbook))

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        return self.data[item]

    def get_carrier_data(self, workbook):
        sheet = workbook.sheet_by_index(0)
        for row_number in xrange(1, sheet.nrows):
            row = sheet.row_values(row_number)
            name = row[self.name_column]
            city = row[self.city_column]
            street = row[self.street_column]
            country = row[self.country_column]
            company_id = row[self.company_id_column]
            agreement_versions = row[self.agreements_column]
            if not any([city, name, company_id, country, street]):
                continue
            yield CarrierData(
                row_number, name, city, street, country, company_id, agreement_versions)

    def is_valid(self):
        sheet = self.workbook.sheet_by_index(0)
        header_row = sheet.row_values(0)

        mandatory_fields = {
            'Company': CarrierExcel.name_column,
            'Town': CarrierExcel.city_column,
        }

        for field, column in mandatory_fields.iteritems():
            if field not in header_row[column]:
                return False

        return True

    def save(self):
        workbook = copy_workbook(self.workbook)
        sheet = workbook.get_sheet(0)
        for data in self.data:
            row = data.row_number
            sheet.write(row, self.company_id_column, data.company_id)
            sheet.write(row, self.agreements_column, data.agreement_versions)
        contents = StringIO()
        workbook.save(contents)
        return contents.getvalue()
