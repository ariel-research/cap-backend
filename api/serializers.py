from abc import ABC

from rest_framework import serializers
from .models import Course, Course_group, Student, Ranking, Result, Office
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class CourseSerializer(serializers.ModelSerializer):
    course_group = serializers.StringRelatedField()
    class Meta:
        model = Course
        fields = ['course_id', 'Semester', 'lecturer', 'capacity', 'day', 'time_start', 'time_end', 'course_group']


class Course_groupSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)

    class Meta:
        model = Course_group
        fields = ['id', 'name', 'is_elective', 'office', 'courses']


class Course_groupMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course_group
        fields = ['id', 'name']


class StudentSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)

    class Meta:
        model = Student
        fields = ['student_id', 'user', 'amount_elective', 'office', 'courses']


class OfficeSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True)
    courses = Course_groupSerializer(many=True)

    class Meta:
        model = Office
        fields = ['office_id', 'name', 'user', 'start_time', 'end_time', 'students', 'courses']


class RankingSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()

    class Meta:
        model = Ranking
        fields = ['id', 'rank', 'student', 'course_group']


class RankingMiniSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=70)
    score = serializers.IntegerField()


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'student', 'course', 'selected']
