from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from .models import *


@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    pass


@admin.register(StatusStaff)
class StatusStaffAdmin(ImportExportModelAdmin):
    pass