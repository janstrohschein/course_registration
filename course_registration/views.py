from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from course_registration.models import Course, User_Course_Registration

class CourseList(generic.ListView):
    model = Course
    template_name = 'course_registration/course_list.html'
    context_object_name = 'course_list'
    success_url = '/course_mgmt/courses'
    paginate_by = 10

    def get_queryset(self):
        new_context = Course.objects.filter(course_status='active')
        return new_context

class CourseDetail(generic.DetailView):
    model = Course
    template_name = 'course_registration/course_detail.html'
    fields = '__all__'



class CourseRegister(generic.CreateView):
    model = User_Course_Registration
    fields = '__all__'
    template_name = 'course_registration/course_register.html'
    context_object_name = 'course'
    success_url = '/course_mgmt/courses'
    sucess_message = 'Registered successfully!'

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(CourseRegister, self).get_context_data(**kwargs)

        # additional context

        # order_by() necessary cuz there is a bug with Meta Ordering in the Model and .distinct()
        SKZQuerySet = SKZ.objects.all()
        SKZList = []

        for mySKZ in SKZQuerySet:
            row = [mySKZ.SKZ, mySKZ.devType.parameter1, mySKZ.devType.parameter2, mySKZ.devType.parameter3]
            SKZList.append(row)

        context['SKZ'] = SKZList

        return context
