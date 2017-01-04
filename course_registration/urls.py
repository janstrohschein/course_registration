from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^course/list$', views.CourseList.as_view(), name='course_list'),
    url(r'^course/list/(?P<page>\d+)$', views.CourseList.as_view(), name='course_list'),
]