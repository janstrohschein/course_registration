from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^courses$', views.CourseList.as_view(), name='course_list'),
    url(r'^courses/(?P<page>\d+)$', views.CourseList.as_view(), name='course_list'),

    #url(r'^course/(?P<slug>[-\w]+)/$', views.CourseDetail.as_view(), name='course_detail'),
    url(r'^course/(?P<slug>[-\w]+)/$', views.CourseDetail.as_view(), name='course_detail'),

    url(r'^my_courses$', views.StudentCourses.as_view(), name='my_courses'),

    url(r'^teacher_courses$', views.TeacherCourses.as_view(), name='teacher_courses'),
    url(r'^teacher_courses/add_course$', views.TeacherCoursesAdd.as_view(), name='teacher_courses_add'),
    url(r'^teacher_courses/add_iteration$', views.TeacherIterationAdd.as_view(), name='teacher_iteration_add'),
    url(r'^teacher_courses/add_field$', views.TeacherFieldAdd.as_view(), name='teacher_field_add'),

    url(r'^teacher_courses/delete_iteration/(?P<pk>\d+)$', views.TeacherIterationDelete.as_view(), name='teacher_iteration_delete'),

    url(r'^teacher_courses_detail/(?P<slug>[-\w]+)$', views.TeacherCoursesDetail.as_view(), name='teacher_courses_detail'),
    url(r'^student_courses_detail/(?P<slug>[-\w]+)/(?P<user>\d+)$', views.StudentCoursesDetail.as_view(), name='student_courses_detail'),
    

]