from django.shortcuts import render
from django.views import generic
import sys
from django.contrib.auth import get_user, authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from course_registration.models import Course, User_Course_Registration, User_Course_Progress, Field, Progress
from django.contrib.auth.models import User
from course_registration.forms import MyUserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from course_registration.ExcelWriter import ExcelWriter
from collections import OrderedDict


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

    def form_valid(self, form):
        valid = super(UserAdd, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid


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


class TeacherCoursesAdd(generic.CreateView):
    model = Course
    template_name = 'course_registration/course_add.html'
    fields = ('course_name', 'course_progress', 'seats_max', 'required_fields')
    success_url = '/course_mgmt/teacher_courses'

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='teacher').count() == 1))
    def dispatch(self, *args, **kwargs):
        return super(TeacherCoursesAdd, self).dispatch(*args, **kwargs)

    def post(self, request, **kwargs):
        att = {}
        att['course_name'] = request.POST['course_name']
        att['course_teacher'] = get_user(request)
        att['course_progress'] = Progress.objects.get(id = request.POST['course_progress'])
        att['seats_max'] = request.POST['seats_max']
        course = Course.objects.create(**att)
        course.required_fields.add(*request.POST.getlist('required_fields'))

        return HttpResponseRedirect('/course_mgmt/teacher_courses')


class TeacherCoursesDetail(SuccessMessageMixin, generic.DetailView):
    model = User_Course_Registration
    template_name = 'course_registration/teacher_courses_detail.html'
    context_object_name = 'student_list'

    def get_success_url(self, request, *args, **kwargs):

        return '/course_mgmt/teacher_courses_detail/' + kwargs['slug']

    def get(self, request, *args, **kwargs):
        course = Course.objects.get(slug=kwargs['slug'])
        progress = Progress.objects.all()
        fields = course.required_fields.all()
        course_details = User_Course_Registration.objects.filter(course_id =course.id).distinct()
        student_list = {}
        for entry in course_details:
            if entry.user_id_id not in student_list:
                student_list[entry.user_id_id] = {}
            student_list[entry.user_id_id][entry.field_id_id] = entry.field_value


        return render(request, 'course_registration/teacher_courses_detail.html', \
                      {'course': course, 'student_list': student_list, 'field_list': fields, 'progress_list': progress})

    def post(self, request, *args, **kwargs):

        course = Course.objects.get(slug=kwargs['slug'])
        progress = Progress.objects.all()
        fields = course.required_fields.all()
        course_details = User_Course_Registration.objects.filter(course_id =course.id).distinct().values()
        student_list = {}

        field_list = []
        for field in fields:
            field_list.append(str(field))

        for entry in course_details:
            if entry['user_id_id'] not in student_list:
                student_list[entry['user_id_id']] = {}
            student_list[entry['user_id_id']][str(entry['field_id_id'])] = entry['field_value']

        for student in student_list:
            student_list[student] = sorted(student_list[student].items())

        new_excel = ExcelWriter()
        new_excel.write_student_list(course, field_list, student_list)
        new_excel.out_wb.close()

        messages.success(request, 'Export finished!')

        # sets filename
        filename = str(course) + '.xlsx'

        """sets the file content type an as excel spreadsheet,
        and sets it to be returned as a http response"""
        # returns the file
        response = HttpResponse(new_excel.output.getvalue(), content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response

