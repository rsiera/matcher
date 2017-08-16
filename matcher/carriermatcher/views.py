import json
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, TemplateView, DetailView

from .forms import MatchingRequestForm, MatchCompanyForm, \
    MatchedCompanyFormset
from .models import MatchingRequest


class MatchingRequestDetailView(TemplateView):
    template_name = 'carriermatcher/matched_carriers_details.html'

    def get(self, request, *args, **kwargs):
        formset = MatchedCompanyFormset(self.matching_request)
        return self.render(formset)

    def post(self, request, *args, **kwargs):
        formset = MatchedCompanyFormset(
            self.matching_request, data=request.POST)
        if not formset.is_valid():
            return self.render(formset)
        formset.save()
        return redirect('carriermatcher:matching_request_download', self.matching_request.pk)

    def render(self, formset):
        return self.render_to_response({'formset': formset})

    @property
    def matching_request(self):
        if not hasattr(self, '_matching_request'):
            pk = self.kwargs['pk']
            self._matching_request = get_object_or_404(MatchingRequest, pk=pk)
        return self._matching_request

matching_request_detail = staff_member_required(MatchingRequestDetailView.as_view())


class DownloadExcel(DetailView):
    model = MatchingRequest
    template_name = 'carriermatcher/matched_carriers_download.html'

matching_request_download = staff_member_required(DownloadExcel.as_view())


class CreateMatchingRequestView(CreateView):
    template_name = 'carriermatcher/create_matching_request.html'
    form_class = MatchingRequestForm

    def get_form_kwargs(self):
        kwargs = super(CreateMatchingRequestView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('carriermatcher:matching_request_detail', args=(self.object.pk,))

create_matching_request = staff_member_required(CreateMatchingRequestView.as_view())


@staff_member_required
def match_company(request):
    form = MatchCompanyForm(request.GET)
    if not form.is_valid():
        return JsonReponse(form.errors, status=400)
    content = {'matches': form.match()}
    return JsonReponse(content)


class JsonReponse(HttpResponse):

    def __init__(self, content, status=200):
        if isinstance(content, dict):
            content = json.dumps(content)
        content_type = 'application/json'
        super(JsonReponse, self).__init__(
            content, status=status, content_type=content_type)
