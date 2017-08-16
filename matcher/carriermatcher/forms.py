from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.formsets import BaseFormSet

from .excel_models import CarrierExcel
from .models import MatchingRequest
from .solr_client import SolrClient


class MatchingRequestForm(forms.ModelForm):

    class Meta:
        model = MatchingRequest
        fields = ('uploaded',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(MatchingRequestForm, self).__init__(*args, **kwargs)

    def clean_uploaded(self):
        uploaded = self.cleaned_data['uploaded']
        try:
            excel = CarrierExcel(uploaded.read())
        except Exception as e:
            raise ValidationError(message='Not appropriate file content: %s' % e)
        else:
            if not excel.is_valid():
                raise ValidationError(message='Not appropriate file content')
        return uploaded

    def save(self, commit=True):
        self.instance.user = self.user
        return super(MatchingRequestForm, self).save(commit)


class MatchCompanyForm(forms.Form):
    name = forms.CharField(required=True)
    city = forms.CharField(required=True)

    def match(self):
        name = self.cleaned_data['name']
        city = self.cleaned_data['city']
        client = SolrClient()
        results = client.carriers_by_name_and_city(name, city)
        return results


class MatchedCompanyForm(forms.Form):
    row_number = forms.IntegerField(widget=forms.HiddenInput)
    company_id = forms.IntegerField(required=False, widget=forms.HiddenInput(
        attrs={'class': 'carrier-id'}
    ))
    agreement_id = forms.CharField(required=False, widget=forms.HiddenInput(
        attrs={'class': 'agreement-id'}
    ))

    def __init__(self, *args, **kwargs):
        super(MatchedCompanyForm, self).__init__(*args, **kwargs)
        self.carrier = None

    def save(self):
        self.carrier.company_id = self.cleaned_data['company_id']
        self.carrier.agreement_versions = self.cleaned_data['agreement_id']


class MatchedCompanyFormset(BaseFormSet):
    form = MatchedCompanyForm
    extra = 0
    can_order = False
    can_delete = False
    min_num = None
    max_num = None
    absolute_max = 1000

    def __init__(self, matching_request, data=None):
        self.matching_request = matching_request
        self.carrier_excel = matching_request.carrier_excel
        initial = [item.attrs() for item in self.carrier_excel]
        super(MatchedCompanyFormset, self).__init__(data=data, initial=initial)

    def add_fields(self, form, index):
        form.carrier = self.carrier_excel[index]

    def save(self):
        for form in self.forms:
            form.save()
        content = self.carrier_excel.save()
        name = 'carrierlist-%d.xls' % self.matching_request.pk
        self.matching_request.uploaded.save(name, SimpleUploadedFile(name, content))
