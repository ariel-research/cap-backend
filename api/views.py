from django.shortcuts import render
from rest_framework import viewsets, status
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Course_group, Student, Ranking, Result, Office
from django.contrib.auth.models import User
from .serializers import CourseSerializer, Course_groupSerializer, Course_groupMiniSerializer, StudentSerializer, \
    RankingSerializer, ResultSerializer, UserSerializer, OfficeSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class Course_groupViewSet(viewsets.ModelViewSet):
    queryset = Course_group.objects.all()
    serializer_class = Course_groupSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['GET'])
    def get_course_group(self, request):
        user = request.user
        student_office = Student.objects.get(user=user).office
        course_group = Course_group.objects.filter(is_elective=True).filter(office=student_office)
        serializer = Course_groupSerializer(course_group, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_last_rating(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        student_office = Student.objects.get(user=user).office
        ranking = Ranking.objects.filter(student=student).filter(course_group__is_elective=True) \
            .filter(course_group__office=student_office).order_by('rank')
        if len(ranking) == 0:  # the user not rank his courses
            courses = Course_group.objects.filter(is_elective=True) \
                .filter(office=student_office)
            serializer = Course_groupMiniSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:  # the user rank his courses, show his last rank
            courses = []
            for rank in ranking:
                courses.append(Course_group.objects.get(name=rank.course_group.name))
            serializer = Course_groupSerializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        response = {'message': 'לא ניתן לקבל קבוצות קורסים באופן זה'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['GET'])
    def get_semester_a(self, request):
        user = request.user
        student_office = Student.objects.get(user=user).office
        courses = Course.objects.filter(Semester="א").filter(course_group__office=student_office)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_semester_b(self, request):
        user = request.user
        student_office = Student.objects.get(user=user).office
        courses = Course.objects.filter(Semester="ב").filter(course_group__office=student_office)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_semester_s(self, request):
        user = request.user
        student_office = Student.objects.get(user=user).office
        courses = Course.objects.filter(Semester="ק").filter(course_group__office=student_office)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['GET'])
    def student_or_office(self, request):
        user = request.user
        try:
            student = Student.objects.get(user=user)
            return Response(1, status=status.HTTP_200_OK)  # 1 means student
        except Student.DoesNotExist:
            try:
                office = Office.objects.get(user=user)
                return Response(2, status=status.HTTP_200_OK)  # 2 means office
            except Office.DoesNotExist:
                return Response(3, status=status.HTTP_200_OK)  # 3 means this user is not student and not office


class OfficeViewSet(viewsets.ModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['GET'])
    def get_time(self, request):
        tz_now = timezone.localtime(timezone.now())
        user = request.user
        office = Student.objects.get(user=user).office
        start_time = office.start_time
        end_time = office.end_time
        # if the ranking time has not started
        if start_time >= tz_now:
            timestamp_str = start_time.strftime(" %H:%M:%S ") + "בשעה" + start_time.strftime(" %d/%m/%Y")
            text = timestamp_str + ' הדירוג יפתח ב: '
            response = {'message': text, 'value': 0}
            return Response(response, status=status.HTTP_200_OK)
        # if the ranking ended
        if end_time < tz_now:
            response = {'message': 'הדירוג נסגר', 'value': 0}
            return Response(response, status=status.HTTP_200_OK)
        # if this is the ranking time
        current_time = end_time - tz_now
        hours = int(((end_time - tz_now).total_seconds() / 60.0 - 180) / 60)
        minutes = int(((end_time - tz_now).total_seconds() / 60.0 - 180) % 60)
        time = str(hours) + ":" + str(minutes)
        response = {'message': time, 'value': 1}
        return Response(response, status=status.HTTP_200_OK)


class RankingViewSet(viewsets.ModelViewSet):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

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
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
