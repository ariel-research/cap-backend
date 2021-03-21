from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Course_group, Student, Ranking, Result, Office
from django.contrib.auth.models import User
from .serializers import CourseSerializer, Course_groupSerializer, StudentSerializer, RankingSerializer, \
    ResultSerializer, UserSerializer, OfficeSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class Course_groupViewSet(viewsets.ModelViewSet):
    queryset = Course_group.objects.all()
    serializer_class = Course_groupSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=False, methods=['GET'])
    def get_last_rating(self, request):
        user = request.user
        ranking = Ranking.objects.filter(student=user.id).order_by('rank')
        if len(ranking) == 0:  # the user not rank his courses
            courses = Course_group.objects.all()
            serializer = Course_groupSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:  # the user rank his courses, show his last rank
            courses = []
            for rank in ranking:
                courses.append(Course_group.objects.get(name=rank.course_group.name))
            serializer = Course_groupSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=False, methods=['GET'])
    def get_semester_a(self, request):
        courses = Course.objects.filter(Semester="א")
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_semester_b(self, request):
        courses = Course.objects.filter(Semester="ב")
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_semester_s(self, request):
        courses = Course.objects.filter(Semester="ק")
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class OfficeViewSet(viewsets.ModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer


class RankingViewSet(viewsets.ModelViewSet):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=False, methods=['POST'])
    def rank_courses(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        is_rated = Ranking.objects.filter(student=student).order_by('rank')
        ranking = request.data['ranks']
        if len(is_rated) == 0:  # the user not rank his courses (create)
            for index, movie_rank in enumerate(ranking):
                course = Course_group.objects.get(name=movie_rank['name'])
                Ranking.objects.create(course_group=course, student=student, rank=index + 1)
            return Response('Ranking created', status=status.HTTP_200_OK)
        else:  # the user rank his courses (update)
            for index, movie_rank in enumerate(ranking):
                last_rank = Ranking.objects.get(course_group=movie_rank['id'], student=student)
                last_rank.rank = index + 1
                last_rank.save()
            return Response('Ranking updated', status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        response = {'message': 'לא ניתן לעדכן דירוג באופן זה'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        response = {'message': 'לא ניתן ליצור דירוג באופן זה'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )


