from abc import ABC

from rest_framework import serializers
from .models import Course, Course_group, Student, Ranking, Result, Office, Course_time
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password']
        extra_kwargs = {'password2': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = User.objects.create(      
            username=validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        user.is_active = False        

        user.set_password(validated_data['password'])
        #user.save()
        #Token.objects.create(user=user)
        return user


    def update(self,validated_data):
         user = User.objects.update(      
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
        )
        #user.set_password(validated_data['password'])
        #return user
        
class Course_groupMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course_group
        fields = ['id', 'name']

class CourseSerializer(serializers.ModelSerializer):
    course_group = Course_groupMiniSerializer()

    class Meta:
        model = Course
        fields = ['id','course_id', 'Semester', 'lecturer', 'capacity', 'day', 'time_start', 'time_end', 'course_group']

class Course_timeSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = Course_time
        fields = ['day','time_start','time_end','class_type','course']

class CourseMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_id']


class Course_groupSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)

    class Meta:
        model = Course_group
        fields = ['id', 'name', 'is_elective', 'office', 'courses']


class StudentSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)

    class Meta:
        model = Student
        fields = ['student_id', 'user', 'amount_elective', 'office', 'courses', 'program']

class StudentUserSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)
    user = UserSerializer()
    class Meta:
        model = Student
        fields = ['student_id', 'user', 'amount_elective', 'office', 'courses', 'program']


class StudentMiniSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()


class OfficeSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True)
    courses = Course_groupSerializer(many=True)

    class Meta:
        model = Office
        fields = ['office_id', 'name', 'user', 'start_time', 'end_time', 'students', 'courses']


class RankingSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    course = serializers.CharField(max_length=70)

    class Meta:
        model = Ranking
        fields = ['id', 'rank', 'student', 'course','is_acceptable']


class RankingMiniSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=70)
    score = serializers.IntegerField()
    overlap = serializers.BooleanField()
    lecturer = serializers.CharField(max_length=70)
    day = serializers.CharField(max_length=70)
    semester = serializers.CharField(max_length=70)
    time_start = serializers.CharField(max_length=70)
    time_end = serializers.CharField(max_length=70)
    id = serializers.CharField(max_length=70)
    is_acceptable = serializers.BooleanField()
    course_time = Course_timeSerializer(many=True)

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'student', 'course', 'selected']
