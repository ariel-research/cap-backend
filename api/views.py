import json

import pytz
from django.db import transaction
from django.shortcuts import render
from datetime import timedelta, datetime, date
from rest_framework import viewsets, status
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Course_group, Student, Ranking, Result, Office
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializers import CourseSerializer, Course_groupSerializer, Course_groupMiniSerializer, StudentSerializer, \
    RankingSerializer, ResultSerializer, UserSerializer, OfficeSerializer, RankingMiniSerializer


# take second element for sort
def take_score(elem):
    return elem.get("score")


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
            default_ranking = []
            for course in courses:
                rank = {"name": course.name, "score": 45}
                default_ranking.append(rank)
            serializer = RankingMiniSerializer(default_ranking, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:  # the user rank his courses, show his last rank
            user_ranking = []
            for rank in ranking:
                rank = {"name": rank.course_group.name, "score": rank.rank}
                user_ranking.append(rank)
            user_ranking.sort(key=take_score, reverse=True)
            serializer = RankingMiniSerializer(user_ranking, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        response = {'message': 'לא ניתן לקבל קבוצות קורסים באופן זה'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['POST'])
    def create_objects(self, request):
        user = request.user
        office = Office.objects.get(user=user)
        # Read the JSON
        courses_string = request.data['courses']
        try:
            courses = json.loads(courses_string)
        except json.decoder.JSONDecodeError as e:
            return Response(str(e), status=status.HTTP_200_OK)
        # Create a Django model object for each object in the JSON
        try:
            with transaction.atomic():
                for course in courses:
                    print(course['start_time'])
                    try:
                        course_group = Course_group.objects.get(name=course['name'])
                        Course.objects.create(course_id=course['id'], Semester=course['semester'],
                                              lecturer=course['lecturer'],
                                              day=course['day'], capacity=course['capacity'],
                                              time_start=course['start_time'],
                                              time_end=course['end_time'], course_group=course_group)
                    except Course_group.DoesNotExist:
                        course_group = Course_group.objects.create(name=course['name'],
                                                                   is_elective=course['is_elective'], office=office)
                        Course.objects.create(course_id=course['id'], Semester=course['semester'],
                                              lecturer=course['lecturer'],
                                              day=course['day'], capacity=course['capacity'],
                                              time_start=course['start_time'],
                                              time_end=course['end_time'], course_group=course_group)
                return Response("הקורסים נוצרו", status=status.HTTP_200_OK)


        except KeyError as e:
            return Response("KeyError" + str(e), status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_semester_a(self, request):
        user = request.user
        student_office = Student.objects.get(user=user).office
        courses = Course.objects.filter(Semester="א").filter(course_group__office=student_office).filter(
            course_group__is_elective=True)
        courses_semester_a = [[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]]
        serializer = CourseSerializer(courses, many=True)
        for course in serializer.data:
            time_start = datetime.strptime(course['time_start'], '%H:%M:%S').time()
            time_end = datetime.strptime(course['time_end'], '%H:%M:%S').time()
            duration = str(datetime.combine(date.today(), time_end) - datetime.combine(date.today(), time_start))
            course['duration'] = duration[0]
            for i in range(14):
                start_hour = i + 8
                start_table = '0' + str(start_hour) + ':00'
                if start_hour > 9:
                    start_table = str(start_hour) + ':00'
                if time_start == datetime.strptime(start_table, '%H:%M').time():
                    if course['day'] == 'א':
                        courses_semester_a[i][5].append(course)
                    if course['day'] == 'ב':
                        courses_semester_a[i][4].append(course)
                    if course['day'] == 'ג':
                        courses_semester_a[i][3].append(course)
                    if course['day'] == 'ד':
                        courses_semester_a[i][2].append(course)
                    if course['day'] == 'ה':
                        courses_semester_a[i][1].append(course)
                    if course['day'] == 'ו':
                        courses_semester_a[i][0].append(course)
        return Response(courses_semester_a, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_semester_b(self, request):
        user = request.user
        student_office = Student.objects.get(user=user).office
        courses = Course.objects.filter(Semester="ב").filter(course_group__office=student_office).filter(
            course_group__is_elective=True)
        courses_semester_a = [[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]]
        serializer = CourseSerializer(courses, many=True)
        for course in serializer.data:
            time_start = datetime.strptime(course['time_start'], '%H:%M:%S').time()
            time_end = datetime.strptime(course['time_end'], '%H:%M:%S').time()
            duration = str(datetime.combine(date.today(), time_end) - datetime.combine(date.today(), time_start))
            course['duration'] = duration[0]
            for i in range(14):
                start_hour = i + 8
                start_table = '0' + str(start_hour) + ':00'
                if start_hour > 9:
                    start_table = str(start_hour) + ':00'
                if time_start == datetime.strptime(start_table, '%H:%M').time():
                    if course['day'] == 'א':
                        courses_semester_a[i][5].append(course)
                    if course['day'] == 'ב':
                        courses_semester_a[i][4].append(course)
                    if course['day'] == 'ג':
                        courses_semester_a[i][3].append(course)
                    if course['day'] == 'ד':
                        courses_semester_a[i][2].append(course)
                    if course['day'] == 'ה':
                        courses_semester_a[i][1].append(course)
                    if course['day'] == 'ו':
                        courses_semester_a[i][0].append(course)
        return Response(courses_semester_a, status=status.HTTP_200_OK)

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

    @action(detail=False, methods=['POST'])
    def create_objects(self, request):
        user = request.user
        office = Office.objects.get(user=user)
        # Read the JSON
        students_string = request.data['students']
        try:
            students = json.loads(students_string)
        except json.decoder.JSONDecodeError:
            return Response('The file is invalid', status=status.HTTP_200_OK)
        # Create a Django model object for each object in the JSON
        try:
            with transaction.atomic():
                for student in students:

                    student_user = User.objects.create_user(student['name'], student['email'], student['password'])
                    Token.objects.create(user=student_user)
                    student_obj = Student.objects.create(user=student_user, student_id=student['id'],
                                                         amount_elective=student['amount_elective'], office=office)
                    for course in student['courses']:
                        cur = Course.objects.get(course_id=course)
                        student_obj.courses.add(cur)
        except KeyError as e:
            return Response("KeyError" + str(e), status=status.HTTP_200_OK)
        return Response('Students created', status=status.HTTP_200_OK)


class OfficeViewSet(viewsets.ModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['GET'])
    def algo(self, request):
        user = request.user
        office = Office.objects.get(user=user)
        student_set = Student.objects.filter(office=office)
        course_set = Course.objects.filter(course_group__office=office)
        serializer = StudentSerializer(student_set, many=True)
        print(serializer.data)
        print(student_set.values())
        print(list(course_set))
        return Response("OK", status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_time(self, request):
        tz_now = timezone.localtime(timezone.now())
        user = request.user
        office = Student.objects.get(user=user).office
        start_time = office.start_time + timedelta(hours=3)
        end_time = office.end_time + timedelta(hours=3)
        # if the ranking time has not started
        if start_time >= tz_now:
            timestamp_str = start_time.strftime(" %d/%m") + " בשעה " + start_time.strftime(" %H:%M ")
            text = 'הדירוג יפתח ב: ' + timestamp_str
            response = {'message': text, 'value': 0}
            return Response(response, status=status.HTTP_200_OK)
        # if the ranking ended
        if end_time < tz_now:
            response = {'message': 'הדירוג נסגר', 'value': 0}
            return Response(response, status=status.HTTP_200_OK)
        # if this is the ranking time
        current_time = end_time - tz_now
        # hours = int(((end_time - tz_now).total_seconds() / 60.0 - 180) / 60)
        # minutes = int(((end_time - tz_now).total_seconds() / 60.0 - 180) % 60)
        timestamp_str = end_time.strftime(" %d/%m") + " בשעה " + end_time.strftime(" %H:%M ")
        time = 'הדירוג ייסגר ב: ' + timestamp_str
        response = {'message': time, 'value': 1}
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def set_date(self, request):
        user = request.user
        start_date = request.data['StartDate'].split('-')
        end_date = request.data['EndDate'].split('-')
        start_time = request.data['StartTime'].split(':')
        end_time = request.data['EndTime'].split(':')
        start_datetime = datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]), int(start_time[0]),
                                  int(start_time[1]), 0, tzinfo=pytz.UTC) - timedelta(hours=3)
        end_datetime = datetime(int(end_date[0]), int(end_date[1]), int(end_date[2]), int(end_time[0]),
                                int(end_time[1]), 0, tzinfo=pytz.UTC) - timedelta(hours=3)
        Office.objects.filter(user=user).update(start_time=start_datetime, end_time=end_datetime)
        return Response("התאריכים התעדכנו", status=status.HTTP_200_OK)


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
        is_positive = 1000 - sum(rank['score'] for rank in ranking)
        if is_positive < 0:
            response = {'message': 'ניתן להשתמש לכל היותר ב-1000 נק'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        if len(is_rated) == 0:  # the user not rank his courses (create)
            for movie_rank in ranking:
                course = Course_group.objects.get(name=movie_rank['name'])
                Ranking.objects.create(course_group=course, student=student, rank=movie_rank['score'])
            return Response('Ranking created', status=status.HTTP_200_OK)
        else:  # the user rank his courses (update)
            for movie_rank in ranking:
                last_rank = Ranking.objects.get(course_group__name=movie_rank['name'], student=student)
                if last_rank.rank != movie_rank['score']:
                    last_rank.rank = movie_rank['score']
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

    @action(detail=False, methods=['GET'])
    def get_results(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        results = Result.objects.filter(student=student).filter(selected=True)
        serializer = ResultSerializer(results, many=True)
        courses = []
        for result in serializer.data:
            courses.append(Course.objects.get(id=result['course']))
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
