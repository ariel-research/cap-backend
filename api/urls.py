from django.contrib import admin
from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import CourseViewSet, Course_groupViewSet, StudentViewSet, RankingViewSet, ResultViewSet, UserViewSet,\
    OfficeViewSet,RegisterView


router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('courses', CourseViewSet, basename='courses')
router.register('course_group', Course_groupViewSet)
router.register('student', StudentViewSet)
router.register('office', OfficeViewSet)
router.register('ranking', RankingViewSet)
router.register('result', ResultViewSet)
router.register('register', RegisterView,basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('accounts/', include('rest_registration.api.urls')),
]
