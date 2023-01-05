from django.utils.translation import gettext_lazy as _
from django.contrib import admin# Need to import this since auth models get registered on import.
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy as DRFToken
admin.site.site_title = _('Django Calories Tracker')
admin.site.site_header = _('Django Calories Tracker')
admin.site.index_title = _('My Django Calories Tracker administration')

admin.site.unregister(DRFToken)
admin.site.unregister(Group)
