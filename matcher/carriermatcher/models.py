from datetime import datetime

from django.conf import settings
from django.db import models

from .excel_models import CarrierExcel

HELP_TEXT = '''
<h3>Only xls files with following structure</h3>
#6. column: Company <br/>
#15. column: Town <br/>
'''


class MatchingRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    uploaded = models.FileField(
        upload_to='matching',
        help_text=HELP_TEXT,
        max_length=250,
    )
    created_at = models.DateTimeField(default=datetime.now)

    @property
    def carrier_excel(self):
        return CarrierExcel(self.uploaded.read())
