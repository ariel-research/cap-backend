from django.contrib import admin
from .models import Course, Course_group, Student, Ranking, Result, Office
from import_export.admin import ImportExportModelAdmin


@admin.register(Course, Course_group, Student, Office, Ranking, Result)
class ViewAdmin(ImportExportModelAdmin):
    pass

