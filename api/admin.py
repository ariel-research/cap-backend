from django.contrib import admin
from .models import Course, Course_group, Student, Ranking, Result, Office, Course_time,Result_info
from import_export.admin import ImportExportModelAdmin


@admin.register(Course, Course_group, Student, Office, Ranking, Result, Course_time,Result_info)
class ViewAdmin(ImportExportModelAdmin):
    pass

