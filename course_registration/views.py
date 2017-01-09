from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
import sys
from django.contrib.auth import get_user
from django.http import HttpResponseRedirect
from course_registration.models import Course, User_Course_Registration, User_Course_Progress, Field, Progress


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
    sucess_message = 'Registered successfully!'

    def post(self, request, *args, **kwargs):
        # get number of required fields
        # if submitted number is equal proceed registration
        course = Course.objects.get(slug=kwargs['slug'])
        count_required_fields = course.required_fields.count()

        # +1 because request.POST contains also the csrf token
        if count_required_fields + 1 == len(request.POST):

        # for every submitted field the field, field value, user and course will
        # be inserted into CourseRegistration
            user =  get_user(request)

            for entry in request.POST:
                if entry != 'csrfmiddlewaretoken':
                    try:
                        field = Field.objects.get(field_name__exact=entry)
                        if field:
                            reg_values = {}
                            reg_values['user_id'] = user
                            reg_values['course_id'] = course
                            reg_values['field_id'] = field
                            reg_values['field_value'] = request.POST[entry]
                            new_reg = User_Course_Registration.objects.get_or_create(**reg_values)

                    except:
                        print(sys.exc_info())

            prog_values = {}
            prog_values['user_id'] = user
            prog_values['course_id'] = course
            prog_values['user_progress_id'] = course.course_progress
            prog_values['progress_reached'] = True
            new_prog = User_Course_Progress.objects.get_or_create(**prog_values)

        return HttpResponseRedirect('/course_mgmt/my_courses')


class UserCourses(generic.DetailView):
    model = User_Course_Progress
    template_name = 'course_registration/my_courses.html'
    context_object_name = 'course_list'
    success_url = '/course_mgmt/my_courses'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        courses = User_Course_Progress.objects.filter(user_id=user).distinct()
        return render(request, 'course_registration/my_courses.html', {'user': user, 'course_list': courses})

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
