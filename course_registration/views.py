from django.shortcuts import render
from django.views import generic
import sys
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from course_registration.models import Course, User_Course_Registration, User_Course_Progress, Field
from django.contrib.auth.models import User
from course_registration.forms import MyUserCreationForm
from django.contrib.messages.views import SuccessMessageMixin


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


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


class CourseDetail(SuccessMessageMixin, generic.DetailView):
    model = Course
    template_name = 'course_registration/course_detail.html'
    fields = '__all__'
    success_message = 'Registered successfully!'

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
            user = get_user(request)
            # if user.pk is None:
            #     user, status = User.objects.get_or_create(username='Anonym', email=request.POST['Email'])

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


class UserCourses(LoginRequiredMixin, generic.DetailView):
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

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='teacher').count() == 1))
    def dispatch(self, *args, **kwargs):
        return super(TeacherCourses, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        teacher = get_user(self.request)
        new_context = Course.objects.filter(course_teacher=teacher)
        return new_context

class TeacherCoursesDetail(generic.DetailView):
    model = User_Course_Registration
    template_name = 'course_registration/teacher_courses_detail.html'
    context_object_name = 'student_list'

    def get(self, request, *args, **kwargs):
        course = Course.objects.get(slug=kwargs['slug'])
        fields = course.required_fields.all()
        course = User_Course_Registration.objects.filter(course_id =course.id).distinct()
        student_list = {}
        for entry in course:
            if entry.user_id_id not in student_list:
                student_list[entry.user_id_id] = {}
            student_list[entry.user_id_id][entry.field_id_id] = entry.field_value


        return render(request, 'course_registration/teacher_courses_detail.html', {'student_list': student_list, 'field_list': fields})

    # def get_queryset(self):
    #     new_context = Course.objects.filter(slug=self.kwargs['slug'])
    #     return new_context
