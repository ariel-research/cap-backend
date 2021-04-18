from django.test import TestCase
from api.models import Course, Course_group, Office, Student
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from api.serializers import Course_groupSerializer
from rest_framework.test import APIClient
from types import SimpleNamespace
from random import shuffle
import json
import datetime
import pytz


class TestViews(TestCase):
    def setUp(self):
        # add users for the office objects
        self.user_office_test1 = User.objects.create_user(username="user_test1", password="19283746")
        self.office_token = Token.objects.create(user=self.user_office_test1)
        user_office_test2 = User.objects.create_user(username="user_test2", password="19283746")
        # add start time and end time for the office objects
        start_time = datetime.datetime(2021, 7, 29, 12, 0, 0, tzinfo=pytz.UTC)
        end_time = datetime.datetime(2021, 7, 31, 12, 0, 0, tzinfo=pytz.UTC)
        # add office objects
        self.office1 = Office.objects.create(office_id="100", name="office_test1", user=self.user_office_test1,
                                             start_time=start_time,
                                             end_time=end_time)
        office2 = Office.objects.create(office_id="99", name="office_test2", user=user_office_test2,
                                        start_time=start_time,
                                        end_time=end_time)
        # add Course_group(elective, office1) objects
        course_group_a = Course_group.objects.create(name="a", office=self.office1, is_elective=True)
        course_group_b = Course_group.objects.create(name="b", office=self.office1, is_elective=True)
        course_group_c = Course_group.objects.create(name="c", office=self.office1, is_elective=True)
        course_group_d = Course_group.objects.create(name="d", office=self.office1, is_elective=True)
        course_group_e = Course_group.objects.create(name="e", office=self.office1, is_elective=True)
        course_group_f = Course_group.objects.create(name="f", office=self.office1, is_elective=True)
        course_group_g = Course_group.objects.create(name="g", office=self.office1, is_elective=True)
        course_group_h = Course_group.objects.create(name="h", office=self.office1, is_elective=True)
        # add Course_group(not elective, office1) objects
        course_group_i = Course_group.objects.create(name="i", office=self.office1, is_elective=False)
        course_group_j = Course_group.objects.create(name="j", office=self.office1, is_elective=False)
        course_group_k = Course_group.objects.create(name="k", office=self.office1, is_elective=False)
        course_group_l = Course_group.objects.create(name="l", office=self.office1, is_elective=False)
        # add Course_group(elective, office2) objects
        course_group_m = Course_group.objects.create(name="m", office=office2, is_elective=True)
        course_group_n = Course_group.objects.create(name="n", office=office2, is_elective=True)
        # add Course_group(not elective, office2) objects
        course_group_o = Course_group.objects.create(name="o", office=office2, is_elective=False)
        course_group_p = Course_group.objects.create(name="p", office=office2, is_elective=False)
        # add start time and end time for the course objects
        time_start_course = datetime.time(10, 00, 00)
        end_time_course = datetime.time(13, 00, 00)
        # add Course objects
        course_1 = Course.objects.create(course_id="101", Semester='א', lecturer="lecturer1", day='א', capacity=35,
                                         time_start=time_start_course, time_end=end_time_course,
                                         course_group=course_group_a)
        course_2 = Course.objects.create(course_id="102", Semester='א', lecturer="lecturer1", day='א', capacity=35,
                                         time_start=time_start_course, time_end=end_time_course,
                                         course_group=course_group_a)
        course_3 = Course.objects.create(course_id="103", Semester='א', lecturer="lecturer2", day='א', capacity=35,
                                         time_start=time_start_course, time_end=end_time_course,
                                         course_group=course_group_b)
        course_4 = Course.objects.create(course_id="104", Semester='ב', lecturer="lecturer2", day='א', capacity=35,
                                         time_start=time_start_course, time_end=end_time_course,
                                         course_group=course_group_b)
        course_5 = Course.objects.create(course_id="105", Semester='ב', lecturer="lecturer3", day='א', capacity=35,
                                         time_start=time_start_course, time_end=end_time_course,
                                         course_group=course_group_c)
        course_6 = Course.objects.create(course_id="106", Semester='ב', lecturer="lecturer3", day='א', capacity=35,
                                         time_start=time_start_course, time_end=end_time_course,
                                         course_group=course_group_c)
        course_7 = Course.objects.create(course_id="107", Semester='א', lecturer="lecturer4", day='א', capacity=35,
                                         time_start=time_start_course, time_end=end_time_course,
                                         course_group=course_group_d)
        course_8 = Course.objects.create(course_id="108", Semester='א', lecturer="lecturer4", day='א', capacity=35,
                                         time_start=time_start_course, time_end=end_time_course,
                                         course_group=course_group_d)
        course_9 = Course.objects.create(course_id="109", Semester='א', lecturer="lecturer5", day='א', capacity=35,
                                         time_start=time_start_course, time_end=end_time_course,
                                         course_group=course_group_e)
        course_10 = Course.objects.create(course_id="110", Semester='ב', lecturer="lecturer5", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_e)
        course_11 = Course.objects.create(course_id="111", Semester='ב', lecturer="lecturer6", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_f)
        course_12 = Course.objects.create(course_id="112", Semester='ב', lecturer="lecturer6", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_f)
        course_13 = Course.objects.create(course_id="113", Semester='א', lecturer="lecturer7", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_g)
        course_14 = Course.objects.create(course_id="114", Semester='א', lecturer="lecturer7", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_g)
        course_15 = Course.objects.create(course_id="115", Semester='א', lecturer="lecturer8", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_h)
        course_16 = Course.objects.create(course_id="116", Semester='ב', lecturer="lecturer8", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_h)
        course_17 = Course.objects.create(course_id="117", Semester='ב', lecturer="lecturer9", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_i)
        course_18 = Course.objects.create(course_id="118", Semester='ב', lecturer="lecturer9", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_j)
        course_19 = Course.objects.create(course_id="119", Semester='א', lecturer="lecturer1", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_k)
        course_20 = Course.objects.create(course_id="120", Semester='א', lecturer="lecturer1", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_l)
        course_21 = Course.objects.create(course_id="121", Semester='א', lecturer="lecturer2", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_m)
        course_22 = Course.objects.create(course_id="122", Semester='ב', lecturer="lecturer2", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_n)
        course_23 = Course.objects.create(course_id="123", Semester='ב', lecturer="lecturer3", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_o)
        course_24 = Course.objects.create(course_id="124", Semester='ב', lecturer="lecturer3", day='א', capacity=35,
                                          time_start=time_start_course, time_end=end_time_course,
                                          course_group=course_group_p)

        self.client = APIClient()
        self.user = User.objects.create_user('admin', 'admin@admin.com', 'admin123')
        self.token = Token.objects.create(user=self.user)
        self.student = Student.objects.create(student_id=205555407, user=self.user, amount_elective=5,
                                              office=self.office1)

    def test_student_or_office(self):
        # student
        self.client.force_login(user=self.user)
        print("start test_student_or_office")
        response = self.client.get('/api/student/student_or_office/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.token))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, 1)
        self.client.logout()
        # office
        self.client.force_login(user=self.user_office_test1)
        response = self.client.get('/api/student/student_or_office/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.office_token))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, 2)
        self.client.logout()
        # not office or student
        just_a_user = User.objects.create_user(username="just_a_user", password="19283746")
        just_a_user_token = Token.objects.create(user=just_a_user)
        self.client.force_login(user=just_a_user)
        response = self.client.get('/api/student/student_or_office/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(just_a_user_token))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, 3)
        self.client.logout()

    def test_create_objects(self):
        self.client.force_login(user=self.user_office_test1)
        json = {
            "students": [
                {
                    "id": "01",
                    "name": "Tom",
                    "password": "19283746",
                    "email": "tom@gmail.com",
                    "amount_elective": 5,
                    "courses": ["117", "120"]
                },
                {
                    "id": "02",
                    "name": "Tami",
                    "password": "19283746",
                    "email": "tami@gmail.com",
                    "amount_elective": 5,
                    "courses": ["117", "118"]
                },
                {
                    "id": "03",
                    "name": "Som",
                    "password": "19283746",
                    "email": "Som@gmail.com",
                    "amount_elective": 5,
                    "courses": ["119", "120"]
                },
            ]
        }
        response = self.client.post('/api/student/create_objects/', {'students': json}
                                    , format='json', HTTP_AUTHORIZATION='Token {}'.format(self.office_token))
        self.assertEquals(response.status_code, 200)
        student_created = Student.objects.get(student_id="01")
        self.assertEquals(student_created.amount_elective, 5)
        self.assertEquals(student_created.user.username, "Tom")
        self.assertEquals(student_created.courses.get(course_id=117).course_id, '117')
        self.client.logout()

    def test_get_time(self):
        self.client.force_login(user=self.user)
        print("start test_get_time")
        # if the ranking time has not started
        response = self.client.get('/api/office/get_time/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.token))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['value'], 0)
        # if the ranking ended
        start_time = datetime.datetime(2021, 4, 7, 12, 0, 0, tzinfo=pytz.UTC)
        end_time = datetime.datetime(2021, 4, 8, 12, 0, 0, tzinfo=pytz.UTC)
        Office.objects.filter(office_id=self.office1.office_id).update(start_time=start_time)
        Office.objects.filter(office_id=self.office1.office_id).update(end_time=end_time)
        response = self.client.get('/api/office/get_time/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.token))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['value'], 0)
        # if this is the ranking time
        end_time = datetime.datetime(2021, 8, 15, 12, 0, 0, tzinfo=pytz.UTC)
        Office.objects.filter(office_id=self.office1.office_id).update(end_time=end_time)
        response = self.client.get('/api/office/get_time/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.token))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data['value'], 1)

    def test_get_course_group(self):
        self.client.force_login(user=self.user)
        print("start test_get_course_group")
        response = self.client.get('/api/course_group/get_course_group/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.token))
        self.assertEquals(response.status_code, 200)
        data = response.render().content
        courses_group = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        course_group_name = []
        for val in courses_group:
            course_group_name.append(val.name)
        self.assertEquals(course_group_name, ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])

    def test_get_course_group_error(self):
        self.client.force_login(user=self.user)
        print("start test_get_course_group_error")
        response = self.client.get('/api/course_group/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.token))
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['message'], 'לא ניתן לקבל קבוצות קורסים באופן זה')

    def test_get_semester_a(self):
        self.client.force_login(user=self.user)
        print("start test_get_semester_a")
        response = self.client.get('/api/courses/get_semester_a/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.token))
        self.assertEquals(response.status_code, 200)
        data = response.render().content
        courses = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        courses_id = []
        for val in courses:
            courses_id.append(val.course_id)
        self.assertEquals(courses_id, ['101', '102', '103', '107', '108', '109', '113', '114', '115', '119', '120'])

    def test_get_semester_b(self):
        self.client.force_login(user=self.user)
        print("start test_get_semester_b")
        response = self.client.get('/api/courses/get_semester_b/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.token))
        self.assertEquals(response.status_code, 200)
        data = response.render().content
        courses = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        courses_id = []
        for val in courses:
            courses_id.append(val.course_id)
        self.assertEquals(courses_id, ['104', '105', '106', '110', '111', '112', '116', '117', '118'])

    def test_ranking(self):
        self.client.force_login(user=self.user)
        print("start test_get_last_rating, the user not rank his courses")
        response = self.client.get('/api/course_group/get_last_rating/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.token))
        self.assertEquals(response.status_code, 200)
        data = response.render().content
        courses_group = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        courses_group_id = []
        for val in courses_group:
            courses_group_id.append(val.id)
        self.assertEquals(courses_group_id, [1, 2, 3, 4, 5, 6, 7, 8])
        print("start test_rank_courses")
        courses_group = Course_group.objects.filter(office__office_id="100").filter(is_elective=True)
        my_list = list(courses_group)
        shuffle(my_list)
        my_list_id = []
        for item in my_list:
            my_list_id.append(item.id)
        serializer_course_group = Course_groupSerializer(my_list, many=True)
        response = self.client.post('/api/ranking/rank_courses/', {'ranks': serializer_course_group.data}, format='json'
                                    , HTTP_AUTHORIZATION='Token {}'.format(self.token))
        self.assertEquals(response.status_code, 200)
        print("start test_get_last_rating, the user rank his courses")
        response = self.client.get('/api/course_group/get_last_rating/', format='json', HTTP_AUTHORIZATION='Token {}'
                                   .format(self.token))
        self.assertEquals(response.status_code, 200)
        data = response.render().content
        courses_group = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        courses_group_id = []
        for val in courses_group:
            courses_group_id.append(val.id)
        self.assertEquals(courses_group_id, my_list_id)

    def test_ranking_errors(self):
        self.client.force_login(user=self.user)
        print("start test_ranking_errors")
        courses_group = Course_group.objects.filter(office__office_id="100").filter(is_elective=True)
        serializer_course_group = Course_groupSerializer(list(courses_group), many=True)
        response = self.client.post('/api/ranking/', {'ranks': serializer_course_group.data}, format='json'
                                    , HTTP_AUTHORIZATION='Token {}'.format(self.token))
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['message'], 'לא ניתן ליצור דירוג באופן זה')
        response = self.client.put('/api/ranking/1/', {'ranks': serializer_course_group.data}, format='json'
                                   , HTTP_AUTHORIZATION='Token {}'.format(self.token))
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data['message'], 'לא ניתן לעדכן דירוג באופן זה')
