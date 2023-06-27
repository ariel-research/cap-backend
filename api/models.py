from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class Office(models.Model):
    office_id = models.CharField(unique=True, max_length=32)
    name = models.CharField(max_length=70, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return "%s" % self.name


class Course_group(models.Model):
    name = models.CharField(max_length=70, unique=True)
    syllabus = models.FileField(upload_to='syllabus/', null=True, blank=True)
    is_elective = models.BooleanField(default=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name="courses", default=1)
    groups = models.IntegerField(null=True,blank=False)
    def __str__(self):
        return self.name


class Course(models.Model):
    Days = (('א', 'א'), ('ב', 'ב'), ('ג', 'ג'), ('ד', 'ד'), ('ה', 'ה'), ('ו', 'ו'))
    Semester_choices = (('א', 'א'), ('ב', 'ב'), ('ק', 'ק'))
    course_id = models.CharField(unique=True, max_length=32)
    Semester = models.CharField(null=True, blank=False, max_length=5, choices=Semester_choices)
    lecturer = models.CharField(max_length=32)
    day = models.CharField(null=True, blank=False, max_length=5, choices=Days)
    capacity = models.IntegerField()
    day = models.CharField(null=True, blank=False, max_length=5, choices=Days)
    time_start = models.TimeField()
    time_end = models.TimeField()
    course_group = models.ForeignKey(Course_group, on_delete=models.CASCADE, related_name="courses")
    

    def __str__(self):
        return str(self.course_id)

    
class Student(models.Model):
    #student_id = models.IntegerField(unique=True, validators=[
    #    RegexValidator(regex='^.{9}$', message='תעודת הזהות חייבת להיות 9 ספרות', code='nomatch')])
    student_id = models.IntegerField(null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE )
    amount_elective = models.IntegerField(null=True,)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name="students", default=1)
    courses = models.ManyToManyField(Course,null=True,)

    def __str__(self):
        return "%s's profile" % str(self.user.email if self.user.email else self.student_id)


class Ranking(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    rank = models.IntegerField()

    class Meta:
        unique_together = (('course', 'student'),)
        index_together = (('course', 'student'),)

    def __str__(self):
        return '%d %s' % (self.student.student_id, self.course.course_group.name)


class Result(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    selected = models.BooleanField()

    class Meta:
        unique_together = (('course', 'student'),)
        index_together = (('course', 'student'),)

    def __str__(self):
        return '%d מספר קורס: %s %s' % (self.student.student_id, self.course.course_id, self.course.course_group.name)