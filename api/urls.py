from django.contrib import admin
from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import CourseViewSet, Course_groupViewSet, StudentViewSet, RankingViewSet, ResultViewSet, UserViewSet,\
    OfficeViewSet,RegisterView
from django_rest_passwordreset.views import ResetPasswordValidateTokenViewSet, ResetPasswordConfirmViewSet, \
    ResetPasswordRequestTokenViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('courses', CourseViewSet, basename='courses')
router.register('course_group', Course_groupViewSet)
router.register('student', StudentViewSet)
router.register('office', OfficeViewSet)
router.register('ranking', RankingViewSet)
router.register('result', ResultViewSet)
router.register('register', RegisterView,basename='register')
router.register(
    r'auth/passwordreset/validate_token',
    ResetPasswordValidateTokenViewSet,
    basename='reset-password-validate'
)
router.register(
    r'auth/passwordreset/confirm',
    ResetPasswordConfirmViewSet,
    basename='reset-password-confirm'
)
router.register(
    r'auth/passwordreset',
    ResetPasswordRequestTokenViewSet,
    basename='reset-password-request'
)




urlpatterns = [
    path('', include(router.urls)),
    path(r'password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    #path('accounts/', include('rest_registration.api.urls')),
    
]
