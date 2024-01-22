from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.conf import settings

class Office(models.Model):
    office_id = models.CharField(unique=True, max_length=32)
    name = models.CharField(max_length=70, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return "%s" % self.name


class Course_group(models.Model):
    name = models.CharField(max_length=70)
    syllabus = models.FileField(upload_to='syllabus/', null=True, blank=True)
    is_elective = models.BooleanField(default=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name="courses", default=1)
    groups = models.IntegerField(null=True,blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'office'], name='office_course')
        ]
    def __str__(self):
        return f'{self.name}-{self.office}'

class Course(models.Model):
    Days = (('א', 'א'), ('ב', 'ב'), ('ג', 'ג'), ('ד', 'ד'), ('ה', 'ה'), ('ו', 'ו'))
    Semester_choices = (('א', 'א'), ('ב', 'ב'), ('ק', 'ק'))
    course_id = models.CharField(unique=True, max_length=32)
    Semester = models.CharField(null=True, blank=False, max_length=5, choices=Semester_choices)
    lecturer = models.CharField(max_length=32)
    capacity = models.IntegerField()
    day = models.CharField(null=True, blank=False, max_length=5, choices=Days)
    time_start = models.TimeField()
    time_end = models.TimeField()
    course_group = models.ForeignKey(Course_group, on_delete=models.CASCADE, related_name="courses")
    

    def __str__(self):
        return f'{self.course_id}/{self.course_group}'


class Course_time(models.Model):
    day_choises = (('א', 'א'), ('ב', 'ב'), ('ג', 'ג'), ('ד', 'ד'), ('ה', 'ה'), ('ו', 'ו'))
    """class Class_Type(models.TextChoices):
        SPLIT = "1", "המשך"
        EXERCISE = "2", "תרגול"""
    class_type_choises = (('המשך', 'המשך'), ('תרגול', 'תרגול'))
    day = models.CharField(null=True, blank=False, max_length=5, choices=day_choises)
    time_start = models.TimeField()
    time_end = models.TimeField()
    class_type = models.CharField(null=True, blank=False, max_length=5,choices=class_type_choises, default='המשך')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}-{self.course}'
    
class Student(models.Model):
    class Program(models.TextChoices):
        BASIC = "1", "BASIC"
        EXCELL = "2", "EXCELLENCE"

    student_id = models.IntegerField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE )
    amount_elective = models.IntegerField(null=True,)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name="students", default=1)
    courses = models.ManyToManyField(Course,blank=True)
    program = models.CharField(max_length=2,choices=Program.choices,null=True,blank=True, default=Program.BASIC)
    feedback = models.TextField(null=True,blank=True)
    def __str__(self):
        return "%s's profile" % str(self.user.email if self.user.email else self.student_id)


class Ranking(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    rank = models.IntegerField()
    is_acceptable = models.BooleanField(null=True,blank=False,default=True)
    result = models.BooleanField(null=True,blank=True,default=False)
    class Meta:
        unique_together = (('course', 'student'),)
        index_together = (('course', 'student'),)

    def __str__(self):
        return f'{self.student.student_id}, {self.course}'


class Result(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    selected = models.BooleanField()

    class Meta:
        unique_together = (('course', 'student'),)
        index_together = (('course', 'student'),)

    def __str__(self):
        return '%d מספר קורס: %s %s' % (self.student.student_id, self.course.course_id, self.course.course_group.name)

class Result_info(models.Model):
    student = models.OneToOneField(Student,on_delete=models.CASCADE,null=False)
    courses_txt = models.TextField()
    explanation = models.TextField()

    def __str__(self):
        return f'{self.student.user.email}'
    