from django.contrib import admin
from .models import Course, Course_group, Student, Ranking, Result, Office, Course_time,Result_info
from import_export.admin import ImportExportModelAdmin


@admin.register(Course, Course_group, Student, Ranking, Result, Course_time,Result_info)
class ViewAdmin(ImportExportModelAdmin):
    pass


class StudentAdmin(admin.ModelAdmin):
    actions = ['export_student_emails']

    def export_student_emails(self, request, queryset):
        from django.http import HttpResponse
        import csv
        selected_office = queryset.first()
        students = Student.objects.filter(office=selected_office)

        # Create a CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_emails.csv"'

        # Create a CSV writer
        csv_writer = csv.writer(response)
        csv_writer.writerow(['Email'])

        for student in students:
            csv_writer.writerow([student.user.email])

        return response

    export_student_emails.short_description = "Export student emails to CSV"


# Register the StudentAdmin class with the Student model
admin.site.register(Office, StudentAdmin)
