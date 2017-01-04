from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from course_registration.models import Course

class CourseList(generic.ListView):
    model = Course
    template_name = 'course_registration/course_list.html'
    context_object_name = 'course_list'
    success_url = '/course_mgmt/course/list'
    paginate_by = 10

    def get_queryset(self):
        new_context = Course.objects.filter(course_status='active')
        return new_context
