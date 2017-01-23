from django.shortcuts import render
from django.views import generic
from collections import OrderedDict
import sys
from django.contrib.auth import get_user, authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from course_registration.models import Course, User_Course_Registration, User_Course_Progress, Field, Progress
from django.contrib.auth.models import User
from course_registration.forms import MyUserCreationForm, TeacherCoursesAddForm, CourseProgressUpdateForm
from django.contrib.messages.views import SuccessMessageMixin
from course_registration.ExcelWriter import ExcelWriter



class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class UserAdd(generic.CreateView):
    form_class = MyUserCreationForm
    template_name = 'course_registration/register.html'
    success_url = 'course_mgmt/courses'
    success_message = 'User created'

    def form_valid(self, form):
        valid = super(UserAdd, self).form_valid(form)
        form.save()
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password')
        user = User.objects.get(username = username)
        authenticate(username=user, password=password)
        login(self.request, user)
        return valid


class CourseList(generic.ListView):
    model = Course
    template_name = 'course_registration/course_list.html'
    context_object_name = 'course_list'
    success_url = '/course_mgmt/courses'
    paginate_by = 10

    def get_queryset(self):
        new_context = Course.objects.filter(course_registration=True)
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
        if course.course_registration == True and count_required_fields + 1 == len(request.POST) and \
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

            prog_values = {'user_id': user,
                           'course_id': course,
                           'user_progress_id': course.course_progress,
                           'progress_reached': True}

            User_Course_Progress.objects.get_or_create(**prog_values)

        return HttpResponseRedirect('/course_mgmt/my_courses')


class UserCourses(LoginRequiredMixin, generic.DetailView):
    model = User_Course_Progress
    template_name = 'course_registration/my_courses.html'
    context_object_name = 'course_list'
    success_url = '/course_mgmt/my_courses'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        user = get_user(request)
        courses = User_Course_Progress.objects.filter(user_id=user, active=True, course_id__course_active=True)
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
        new_context = Course.objects.filter(course_teacher=teacher).order_by('-course_active', 'course_name')
        return new_context

    def post(self, request):
        all_ids = request.POST.getlist('all_ids')

        if 'course_registration_id' in request.POST:
            registration_ids = request.POST.getlist('course_registration_id')
            negative = []
            for key in all_ids:
                if key not in registration_ids:
                    negative.append(key)

            Course.objects.filter(id__in = registration_ids).update(course_registration = True)
            Course.objects.filter(id__in = negative).update(course_registration = False)

        if 'course_active_id' in request.POST:
            active_ids = request.POST.getlist('course_active_id')
            negative = []
            for key in all_ids:
                if key not in active_ids:
                    negative.append(key)

            Course.objects.filter(id__in = active_ids).update(course_active = True)
            Course.objects.filter(id__in = negative).update(course_active = False)

            return HttpResponseRedirect('/course_mgmt/teacher_courses')


class TeacherCoursesAdd(generic.CreateView):
    model = Course
    template_name = 'course_registration/course_add.html'
    form_class = TeacherCoursesAddForm
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


class TeacherCoursesDetail(SuccessMessageMixin, generic.UpdateView):
    model = Course
    template_name = 'course_registration/teacher_courses_detail.html'
    form_class = CourseProgressUpdateForm

    def get(self, request, *args, **kwargs):
        course = Course.objects.get(slug=kwargs['slug'])
        fields = course.required_fields.all()
        course_details = User_Course_Registration.objects.filter(course_id =course.id).order_by('field_id')
        course_progress = list(User_Course_Progress.objects.filter(course_id =course.id, active = True))

        form = CourseProgressUpdateForm(data={'course_progress': course.course_progress_id})
        student_list = OrderedDict()
        for entry in course_details:
            if entry.user_id_id not in student_list:
                student_list[entry.user_id_id] = OrderedDict()
            student_list[entry.user_id_id][entry.field_id_id] = entry.field_value

        for progress in course_progress:
            if progress.user_id_id in student_list:
                student_list[progress.user_id_id]['progress'] = progress.user_progress_id.progress_name
                student_list[progress.user_id_id]['progress_reached'] = progress.progress_reached

        return render(request, 'course_registration/teacher_courses_detail.html', \
                      {'form': form,'course': course, 'student_list': student_list, 'field_list': fields})

    def post(self, request, *args, **kwargs):

        course = Course.objects.get(slug=kwargs['slug'])

        if 'update_course_progress' in request.POST:
            ## write new course progress with request.POST['course_progress']
            old_progress = course.course_progress
            new_progress = Progress.objects.get(id = request.POST['course_progress'])
            course.course_progress = new_progress
            course.save()

            ## write new student progress entry for all students that reached the last "milestone"
            student_list = User_Course_Progress.objects.filter(course_id = course.id, \
                                        active = True, progress_reached = True)
            student_ids = []
            for student in student_list:
                student_ids.append(student.user_id)

                att = {'user_id': student.user_id,
                       'course_id': student.course_id,
                       'user_progress_id': new_progress}
                User_Course_Progress.objects.get_or_create(**att)


            User_Course_Progress.objects.filter(user_id__in = student_ids, course_id = course.id, \
                                                user_progress_id = new_progress).update(active=True)
            ## deactivate old progress, only for students that got an update
            User_Course_Progress.objects.filter(user_id__in = student_ids, course_id = course.id, \
                                                user_progress_id = old_progress).update(active=False)

            return HttpResponseRedirect('/course_mgmt/teacher_courses_detail/' + kwargs['slug'])

        elif 'update_student_progress' in request.POST:
            course_progress = User_Course_Progress.objects.filter(course_id =course.id, active = True)
            all_ids = request.POST.getlist('all_ids')
            student_ids = []
            if 'student_id' in request.POST:
                student_ids = request.POST.getlist('student_id')

            negative = []
            for key in all_ids:
                if key not in student_ids:
                    negative.append(key)

            course_progress.filter(user_id__in = student_ids).update(progress_reached = True)
            course_progress.filter(user_id__in = negative).update(progress_reached = False)


            return HttpResponseRedirect('/course_mgmt/teacher_courses_detail/' + kwargs['slug'])


        elif 'export' in request.POST:
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


class StudentCoursesDetail(generic.View):
    template_name = 'course_registration/student_courses_detail.html'
    context_object_name = 'progress_list'

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id = kwargs['user'])
        request_user = get_user(request)
        course = Course.objects.get(slug=kwargs['slug'])
        progress_list = User_Course_Progress.objects.filter(user_id= user, course_id= course)

        is_user = False
        is_teacher = False

        if request_user == user:
            is_user = True

        if course.course_teacher == request_user:
            is_teacher = True


        return render(request, 'course_registration/student_courses_detail.html', \
                      {'progress_list': progress_list, 'course_user': user, 'course': course, \
                       'is_user': is_user, 'is_teacher': is_teacher})

    def post(self, request, *args, **kwargs):
        all_ids = request.POST.getlist('all_ids')
        progress_ids = []
        if 'progress_id' in request.POST:
            progress_ids = request.POST.getlist('progress_id')

        negative = []
        for key in all_ids:
            if key not in progress_ids:
                negative.append(key)

        User_Course_Progress.objects.filter(id__in = progress_ids).update(progress_reached = True)
        User_Course_Progress.objects.filter(id__in = negative).update(progress_reached = False)

        url = '/course_mgmt/student_courses_detail/' + kwargs['slug'] + '/' + kwargs['user']
        return HttpResponseRedirect(url)
