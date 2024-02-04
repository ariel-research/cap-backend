import collections
import json
import pytz
from django.db import transaction
from datetime import timedelta, datetime, date
from rest_framework import viewsets, status
from django.utils import timezone
from cap import settings
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Course_group, Student, Ranking, Result, Office, Course_time, Result_info
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializers import CourseSerializer, Course_groupSerializer, CourseMiniSerializer, StudentSerializer, \
    RankingSerializer, ResultSerializer, UserSerializer, OfficeSerializer, RankingMiniSerializer, StudentMiniSerializer, \
    StudentUserSerializer, Course_timeSerializer, ResultInfoSerializer
from api.SP_algorithm.main import main
from .forms import StudentForm
import logging
from django.utils.translation import gettext as _


class RegisterView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['GET'])
    def get_user_status(self, request):
        print(request.query_params.get('username'))
        try:
            username= request.query_params.get('username')
            if not User.objects.filter(username = username).exists():
                return Response({'error': 'חשבון לא קיים'}, status=status.HTTP_404_NOT_FOUND)
            elif User.objects.all().get(username= username).is_active:
                return Response({'message': 'אימייל או סיסמא שגויים'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'message': 'נרשמת בעבר אך לא אימתת את חשבונך'}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

                

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    authentication_classes = (SessionAuthentication,)
    queryset= User.objects.all()
    
    @action(detail=False, methods=['GET'])
    def get_user_details(self, request):
        serializer = UserSerializer(request.user)
        return Response({"user":serializer.data}, status=status.HTTP_200_OK) 


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    @action(detail=False, methods=['GET'])
    def get_student_details(self, request):
        print(request,request.user)
        student = Student.objects.get(user=request.user)
        serializer = StudentUserSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)  

    @action(detail=False, methods=['POST'])
    def update_student_details(self, request):
        studentEdited = request.data.get('profile')
        email = studentEdited['user']['email']
        amount_elective = studentEdited['amount_elective']
        student_id = float(studentEdited['student_id'])
        program = studentEdited['program']
        first_name = studentEdited['user']['first_name']
        last_name = studentEdited['user']['last_name']
        try:
            user_obj = User.objects.get(email=email)
            student = Student.objects.get(user=user_obj)
            print(student_id,student.student_id)
            if student.student_id !=student_id and Student.objects.filter(student_id = student_id).exists():
                return Response({"message":"לא ניתן להשתמש במספר תעודת הזהות שהוזן"}, status=status.HTTP_409_CONFLICT)
            student.student_id = student_id
            student.amount_elective = amount_elective
            student.program = program
            user_obj.first_name = first_name
            user_obj.last_name = last_name
            user_obj.save()
            student.save()
            return Response({"message":"הפרטים התעדכנו בהצלחה"}, status=status.HTTP_200_OK) 
        except Exception as e:
            return Response({"message":f"{e} השינויים לא נשמרו"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_allocation(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        try:
            
            with open(settings.MEDIA_ROOT+f'/explanations/allocation.json', "r") as results_file:
                results = file.read()
                with open(settings.MEDIA_ROOT+f'/explanations/{student.student_id}.log', "r") as file:
                    explantion = file.read()
                return Response(explantion, status=status.HTTP_200_OK)
        except FileNotFoundError as e:
                return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)




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
                return Response(3, status=status.HTTP_401_UNAUTHORIZED)  # 3 means this user is not student and not office

    @action(detail=False, methods=['POST'])
    def create_objects(self, request):
        user = request.user
        office = Office.objects.get(user=user)
        # Read the JSON
        students_string = request.data['students']
        try:
            students = json.loads(students_string)
        except json.decoder.JSONDecodeError:
            return Response('The file is invalid', status=status.HTTP_400_BAD_REQUEST)
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
            return Response("KeyError" + str(e), status=status.HTTP_400_BAD_REQUEST)
        return Response('Students created', status=status.HTTP_201_CREATED)


class Course_groupViewSet(viewsets.ModelViewSet):
    queryset = Course_group.objects.all()
    serializer_class = Course_groupSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['GET'])
    def get_course_group(self, request):
        user = request.user
        student_office = Student.objects.get(user=user).office
        course_group = Course_group.objects.filter(is_elective=True).filter(office=student_office)
        serializer = Course_groupSerializer(course_group, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def student_ranking_status(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        if Ranking.objects.filter(student=student).exists():
            return self.get_last_rating(request)
        return Response(False, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'])
    def get_last_rating(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        student_office = Student.objects.get(user=user).office
        ranking = Ranking.objects.filter(student=student).filter(course__course_group__is_elective=True) \
            .filter(course__course_group__office=student_office).order_by('rank')
        student_serializer = StudentSerializer(student, many=False)
        student_courses = student_serializer.data['courses']
        courses = Course.objects.filter(course_group__is_elective=True).filter(course_group__office=student_office)
        default_ranking = []
        user_ranking = []
        for course in courses:
            course_time =  Course_time.objects.filter(course=course.id)
            course_time_serializer = Course_timeSerializer(course_time,many=True)
            if not Ranking.objects.filter(student=student, course=course).exists():
                rank = {"name": course.course_group.name, "lecturer": course.lecturer, "semester": course.Semester,
                        "day": course.day, "time_start": course.time_start, "time_end": course.time_end, "score": 0,
                        "id": course.course_id, 'overlap': False, "is_acceptable": True, "course_time":course_time_serializer.data,
                        "result": False}
                

                for mandatory in student_courses:
                    mandatory_start = datetime.strptime(mandatory['time_start'], '%H:%M:%S').time()
                    mandatory_end = datetime.strptime(mandatory['time_end'], '%H:%M:%S').time()
                    if rank["semester"] == mandatory["Semester"] and rank["day"] == mandatory["day"]:
                        if course.time_start <= mandatory_start < course.time_end:
                            rank['overlap'] = True
                        elif course.time_start < mandatory_end <= course.time_end:
                            rank['overlap'] = True
                        elif course.time_start == mandatory_start and mandatory_end == course.time_end:
                            rank['overlap'] = True
                default_ranking.append(rank)
            else:  # the user rank his courses, show his last rank
                rank = Ranking.objects.get(student=student,course=course)
                course_ser = {"name": rank.course.course_group.name, "lecturer": rank.course.lecturer,
                        "semester": rank.course.Semester, "day": rank.course.day, "time_start": rank.course.time_start,
                        "time_end": rank.course.time_end, "score": rank.rank, "id": rank.course.course_id,
                        "overlap":False, "is_acceptable": rank.is_acceptable,"course_time":course_time_serializer.data,
                        "result": rank.result}
                for mandatory in student_courses:
                    mandatory_start = datetime.strptime(mandatory['time_start'], '%H:%M:%S').time()
                    mandatory_end = datetime.strptime(mandatory['time_end'], '%H:%M:%S').time()
                    if course_ser["semester"] == mandatory["Semester"] and course_ser["day"] == mandatory["day"]:
                        if rank.course.time_start <= mandatory_start < rank.course.time_end:
                            course_ser['overlap'] = True
                        elif rank.course.time_start < mandatory_end <= rank.course.time_end:
                            course_ser['overlap'] = True
                        elif rank.course.time_start == mandatory_start and mandatory_end == rank.course.time_end:
                            course_ser['overlap'] = True
                user_ranking.append(course_ser)
        user_ranking.sort(key= lambda x: x.get('score'), reverse=True)
        user_courses = user_ranking + default_ranking
        user_courses.sort(key=lambda x: not x['is_acceptable'])
        serializer = RankingMiniSerializer(user_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        response = {'message': 'לא ניתן לקבל קבוצות קורסים באופן זה'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (SessionAuthentication,)
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
                    course_group_obj, course_group_created = Course_group.objects.update_or_create(
                            name=course['name'],office=office,
                            defaults={ 'name': course['name'],'is_elective': course['is_elective'],
                            'office': office, 'groups':1},
                        )

                    course_obj, course_created = Course.objects.update_or_create(
                        course_id=course['id'], 
                        defaults={ 'Semester': course['semester'],
                        'lecturer': course['lecturer'],
                        'day': course['day'], 'capacity': course['capacity'],
                        'time_start': course['start_time'],
                        'time_end': course['end_time'], 'course_group': course_group_obj}
                    )
                    
                return Response("הקורסים נוצרו", status=status.HTTP_201_CREATED)


        except KeyError as e:
            return Response("KeyError" + str(e), status=status.HTTP_400_BAD_REQUEST)

    def get_semester(self, request, semester:str):
        user = request.user
        student = Student.objects.get(user=user)
        student_serializer = StudentSerializer(student, many=False)
        student_office = Student.objects.get(user=user).office
        courses = Course.objects.filter(Semester=semester).filter(course_group__office=student_office).filter(
            course_group__is_elective=True)
        serializer = CourseSerializer(courses, many=True)
        mandatory_courses = []
        for course in student_serializer.data['courses']:
            if course['Semester'] == semester:
                course['mandatory'] = True
                mandatory_courses.append(course)
        for course in serializer.data:
            course['mandatory'] = False
        temp = list(serializer.data) + list(mandatory_courses)
        serializer = temp
        courses_semester = [[[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []],
                              [[], [], [], [], [], []], [[], [], [], [], [], []], [[], [], [], [], [], []]]
        days = {'א': 0, 'ב':1, 'ג':2, 'ד': 3, 'ה': 4, 'ו':5}
        #day_choises = (('א', 0), ('ב', 1), ('ג', 2), ('ד', 3), ('ה', 4), ('ו', 5))
        HOUR_OPTIONS = 14 
        for course in serializer:
            course_time =  Course_time.objects.filter(course=course['id'])
            if course_time:
                time_serializer = Course_timeSerializer(course_time, many=True)
                for time in time_serializer.data:
                    time_start = datetime.strptime(time['time_start'], '%H:%M:%S').time()
                    time_end = datetime.strptime(time['time_end'], '%H:%M:%S').time()
                    class_type = time['class_type']
                    for i in range(HOUR_OPTIONS):
                        start_hour = i + 8
                        start_table = '0' + str(start_hour) + ':00'
                        if start_hour > 9:
                            start_table = str(start_hour) + ':00'
                        if time_start == datetime.strptime(start_table, '%H:%M').time():
                            day = time['day']
                            course_freg = collections.OrderedDict(course)
                            course_freg['class_type'] = class_type
                            courses_semester[i][days[day]].append(course_freg)


                
            time_start = datetime.strptime(course['time_start'], '%H:%M:%S').time()
            time_end = datetime.strptime(course['time_end'], '%H:%M:%S').time()
            duration = str(datetime.combine(date.today(), time_end) - datetime.combine(date.today(), time_start))
            course['duration'] = duration[0]
            for i in range(HOUR_OPTIONS):
                start_hour = i + 8
                start_table = '0' + str(start_hour) + ':00'
                if start_hour > 9:
                    start_table = str(start_hour) + ':00'
                if time_start == datetime.strptime(start_table, '%H:%M').time():
                    day = course['day']
                    courses_semester[i][days[day]].append(course)
        return Response(courses_semester, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_semester_a(self, request):
        return self.get_semester(request,'א')
    
    @action(detail=False, methods=['GET'])
    def get_semester_b(self, request):
        return self.get_semester(request,'ב')

    @action(detail=False, methods=['GET'])
    def get_semester_s(self, request):
        return self.get_semester(request,'ק')



class OfficeViewSet(viewsets.ModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)


    @action(detail=False, methods=['GET'])
    def algo(self, request):
        user = request.user
        office = Office.objects.get(user=user)
        student_set = Student.objects.filter(office=office)
        student_serializer = StudentSerializer(student_set, many=True)
        course_set = Course_group.objects.filter(office=office)
        course_serializer = Course_groupSerializer(course_set, many=True)

        # We create a default ranking for students that didn't ranked

        course_set_tmp = Course.objects.filter(course_group__office=office, course_group__is_elective=True)
        course_serializer_tmp = CourseSerializer(course_set_tmp, many=True)
        default_rank = int(1000 / len(course_serializer_tmp.data))

        for index in student_serializer.data:
             s = Student.objects.get(student_id=index['student_id'])
             count_ranking = Ranking.objects.filter(student=s)
             if len(count_ranking) == 0:
                 for co in course_serializer_tmp.data:
                     cg = Course.objects.get(course_id=co['course_id'])
                     Ranking.objects.create(course=cg, student=s, rank=default_rank)

        ranking_set = Ranking.objects.filter(student__office=office)
        ranking_serializer = RankingSerializer(ranking_set, many=True)
        students, courses = main(student_serializer.data, course_serializer.data, ranking_serializer.data)
        for student in students:
            for course in courses:
                if student.if_student_enroll(course.get_name()):
                    s = Student.objects.get(student_id=student.get_id())
                    c = Course.objects.get(course_id=course.get_id())
                    Result.objects.create(course=c, student=s, selected=True)
        return Response("OK", status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def my_students(self, request):
        user = request.user
        office = Office.objects.get(user=user)
        student_set = Student.objects.filter(office=office)
        student_serializer = StudentMiniSerializer(student_set, many=True)
        string_student = "["
        for student in student_serializer.data:
            string_student = string_student + str(student["student_id"]) + ", "
        string_student = string_student[0: len(string_student)-2]
        string_student = string_student + "]"
        return Response(string_student, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def my_courses(self, request):
        user = request.user
        office = Office.objects.get(user=user)
        courses = Course.objects.filter(course_group__office=office)
        courses_serializer = CourseMiniSerializer(courses, many=True)
        string_course = "["
        for course in courses_serializer.data:
            string_course = string_course + str(course["course_id"]) + ", "
        string_course = string_course[0: len(string_course)-2]
        string_course = string_course + "]"
        return Response(string_course, status=status.HTTP_200_OK)


    @action(detail=False, methods=['GET'])
    def get_time(self, request):
        tz_now = timezone.localtime(timezone.now())
        user = request.user
        office = Student.objects.get(user=user).office
        start_time = office.start_time.astimezone(pytz.timezone('Asia/Jerusalem'))
        end_time = office.end_time.astimezone(pytz.timezone('Asia/Jerusalem'))
        # if the ranking time has not started
        if office.start_time > tz_now:
            timestamp_str = start_time.strftime(" %d/%m") + " בשעה " + start_time.strftime(" %H:%M ")
            text = 'הדירוג יפתח ב: ' + timestamp_str
            response = {'message': text, 'value': 0}
            return Response(response, status=status.HTTP_200_OK)
        # if the ranking ended
        if end_time < tz_now:
            response = {'message': 'הדירוג נסגר', 'value': 0, 'feedback': True}
            return Response(response, status=status.HTTP_200_OK)
        # if this is the ranking time
        timestamp_str = end_time.strftime(" %d/%m") + " בשעה " + end_time.strftime(" %H:%M ")
        time = 'הדירוג ייסגר ב: ' + timestamp_str
        response = {'message': time, 'value': 1}
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_dates(self, request):
        user = request.user
        office = Office.objects.get(user=user)
        start_time = office.start_time
        end_time = office.end_time
        year_strftime_start = start_time.strftime("%y")
        month_strftime_start = start_time.strftime("%m")
        day_strftime_start = start_time.strftime("%d")
        hour_strftime_start = start_time.strftime("%H")
        min_strftime_start = start_time.strftime("%M")
        year_strftime_end = end_time.strftime("%y")
        month_strftime_end = end_time.strftime("%m")
        day_strftime_end = end_time.strftime("%d")
        hour_strftime_end = end_time.strftime("%H")
        min_strftime_end = end_time.strftime("%M")
        response = {'year_start': year_strftime_start, 'month_start': month_strftime_start,
                    'day_start': day_strftime_start, 'hour_start': hour_strftime_start, 'min_start': min_strftime_start,
                    'year_end': year_strftime_end, 'month_end': month_strftime_end,
                    'day_end': day_strftime_end, 'hour_end': hour_strftime_end, 'min_end': min_strftime_end}
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def close_ranking(self, request):
        tz_now = timezone.localtime(timezone.now())
        user = request.user
        office = Office.objects.get(user=user)
        end_time = office.end_time
        # if the ranking ended
        if end_time < tz_now + timedelta(hours=3):
            return Response(True, status=status.HTTP_200_OK)
        return Response(False, status=status.HTTP_200_OK)


    @action(detail=False, methods=['POST'])
    def set_date(self, request):
        user = request.user
        start_date = request.data['StartDate'].split('T')
        day_start = start_date[0].split('-')
        time_start = start_date[1].split(':')
        end_date = request.data['EndDate'].split('T')
        day_end = end_date[0].split('-')
        time_end = end_date[1].split(':')
        start_datetime = datetime(int(day_start[0]), int(day_start[1]), int(day_start[2]), int(time_start[0]),
                                  int(time_start[1]), 0, tzinfo=pytz.UTC)
        end_datetime = datetime(int(day_end[0]), int(day_end[1]), int(day_end[2]), int(time_end[0]),
                                int(time_end[1]), 0, tzinfo=pytz.UTC)
        Office.objects.filter(user=user).update(start_time=start_datetime, end_time=end_datetime)
        return Response("התאריכים התעדכנו", status=status.HTTP_200_OK)


class RankingViewSet(viewsets.ModelViewSet):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    @action(detail=False, methods=['POST'])
    def rank_courses(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        ranking = request.data['ranks']
        is_positive = 1000 - sum(rank['score'] for rank in ranking)
        if is_positive < 0:
            response = {'message': 'ניתן להשתמש לכל היותר ב-1000 נק'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        for rank_pair in ranking:
            course = Course.objects.get(course_id=rank_pair['id'])
            obj, created = Ranking.objects.update_or_create(
                course=course, student=student,
                defaults={ 'rank': rank_pair['score'],'is_acceptable':rank_pair['is_acceptable']},
            )
            logging.debug(f'course {course.course_id} created: {created} rank_pair: {rank_pair}')
        return Response('Ranking created', status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        response = {'message': 'לא ניתן לעדכן דירוג באופן זה'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        response = {'message': 'לא ניתן ליצור דירוג באופן זה'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
    logger = logging.getLogger('feedback')
    logger.setLevel(logging.INFO)

    # Create a file handler for the logger
    file_handler = logging.FileHandler('fill-feedback.log')

    # Create a formatter and set it for the file handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)


    @action(detail=False, methods=['POST'])
    def save_results_feedback(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        ranking = request.data['ranks']
        for rank_pair in ranking:
            course = Course.objects.get(course_id=rank_pair['id'])
            Ranking.objects.filter(course_id=course, student=student).update(result=rank_pair['result'])
        self.logger.info(f'The user {user} update a feedback')
        return Response('המשוב נשמר בהצלחה', status=status.HTTP_200_OK)

    

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    authentication_classes = (SessionAuthentication,)
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
        # find ranking for the course
        ranking = Ranking.objects.filter(student=student).filter(course__course_group__is_elective=True).order_by('-rank')
        for course in serializer.data:
            for index, value in enumerate(ranking):
                if str(value.course.course_id) == str(course['course_id']):
                    course['rank'] = index+1
        newlist = sorted(serializer.data, key=lambda k: k['rank'])
        return Response(newlist, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['GET'])
    def get_results_info(self, request):
        user = request.user
        student = Student.objects.get(user=user)
        courses_txt = ''
        explanation = ''
        """if not Result.objects.filter(student=student).exists:
            try:
                with open(settings.MEDIA_ROOT+f'/explanations/allocation.json', "r") as results_file:
                    results = file.read()
                    with open(settings.MEDIA_ROOT+f'/explanations/{student.student_id}.log', "r") as file:
                        explantion = file.read()
            except FileNotFoundError as e:
                    return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)
        """
        try:
            result = Result_info.objects.get(student=student)
            result_serizalizer = ResultInfoSerializer(result)
            courses_txt = result_serizalizer.data['courses_txt']
            explanation = result_serizalizer.data['explanation']
        except Exception as e:
            courses_txt = ''
            explanation = ''
        return Response({'courses_txt':courses_txt,'explanation':explanation},
                        status=status.HTTP_200_OK)


