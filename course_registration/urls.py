from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$', views.Index.as_view(), name='index'),
    url(r'^$', views.CourseList.as_view(), name='course_list'),
]