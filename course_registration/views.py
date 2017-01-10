from django.shortcuts import render
from django.views import generic
import sys
from django.contrib.auth import get_user
from django.http import HttpResponseRedirect
from course_registration.models import Course, User_Course_Registration, User_Course_Progress, Field
from course_registration.forms import MyUserCreationForm


class UserAdd(generic.CreateView):
    form_class = MyUserCreationForm
    template_name = 'course_registration/register.html'
    success_url = '/login/'
    success_message = 'User created'


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

    def post(self, request, **kwargs):
        # get number of required fields
        # if submitted number is equal proceed registration
        course = Course.objects.get(slug=kwargs['slug'])
        count_required_fields = course.required_fields.count()

        # +1 because request.POST contains also the csrf token
        if count_required_fields + 1 == len(request.POST) and \
                course.seats_cur < course.seats_max:

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

            # get_or_create returns the object and information if it was created
            if new_reg[1] == True:
                course.seats_cur += 1
                course.save()

            prog_values = {'user_id': user,
                           'course_id': course,
                           'user_progress_id': course.course_progress,
                           'progress_reached': True}

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

class TeacherCourses(generic.ListView):
    model = Course
    template_name = 'course_registration/teacher_courses.html'
    context_object_name = 'course_list'
    success_url = '/course_mgmt/teacher_courses'
    paginate_by = 10

    def get_queryset(self):
        teacher = get_user(self.request)
        new_context = Course.objects.filter(course_teacher=teacher)
        return new_context
