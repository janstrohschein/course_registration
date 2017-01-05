from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^courses$', views.CourseList.as_view(), name='course_list'),
    url(r'^courses/(?P<page>\d+)$', views.CourseList.as_view(), name='course_list'),
    url(r'^course/(?P<slug>[-\w]+)/$', views.CourseDetail.as_view(), name='course_detail'),
]