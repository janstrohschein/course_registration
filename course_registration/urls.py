from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^courses$', views.CourseList.as_view(), name='course_list'),
    url(r'^courses/(?P<page>\d+)$', views.CourseList.as_view(), name='course_list'),

    url(r'^course/(?P<slug>[-\w]+)/$', views.CourseDetail.as_view(), name='course_detail'),

    url(r'^my_courses$', views.UserCourses.as_view(), name='my_courses'),

    url(r'^teacher_courses$', views.TeacherCourses.as_view(), name='teacher_courses'),
    url(r'^teacher_courses/add$', views.TeacherCoursesAdd.as_view(), name='teacher_courses_add'),

    url(r'^teacher_courses_detail/(?P<slug>[-\w]+)$', views.TeacherCoursesDetail.as_view(), name='teacher_courses_detail'),


]