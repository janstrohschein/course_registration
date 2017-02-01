from django.shortcuts import render
from django.views import generic
from collections import OrderedDict
import sys
from django.contrib.auth import get_user, authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse
from course_registration.models import Course, User_Course_Registration, User_Course_Progress, Field, Progress,\
    Course_Iteration
from django.contrib.auth.models import User
from course_registration.forms import MyUserCreationForm, TeacherCoursesAddForm, CourseProgressUpdateForm
from django.contrib.messages.views import SuccessMessageMixin
from course_registration.ExcelWriter import ExcelWriter


class LoginRequiredMixin(object):
    """
    This Mixin can be used to display views only to logged in users
    """

    @classmethod
    def as_view(cls, **initkwargs):
        """

        :param initkwargs:
        :return:
        """
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


def subtract_ids(request, keyword):
    """
    This function helps reading values from HTML checkboxes.

    Checkboxes that are unchecked are not submitted in a form. The workaround is to create hidden input fields
    with all IDs and subtracting the checked boxes to also get the unchecked boxes.

    :param request:
    :param keyword: the dictionary key to retrieve the positive IDs from request.POST
    :return: two lists with IDs of checked/positive and unchecked/negative entries
    """
    positive_ids = []
    negative_ids = []
    all_ids = request.POST.getlist('all_ids')

    if keyword in request.POST:
        positive_ids = request.POST.getlist(keyword)

    for key in all_ids:
        if key not in positive_ids:
            negative_ids.append(key)

    return positive_ids, negative_ids


class UserAdd(generic.CreateView):
    """
    Adds a new user using djangos auth functionality

    form_valid is overridden to automatically login the user after registration
    """

    form_class = MyUserCreationForm
    template_name = 'course_registration/register.html'
    success_url = 'course_mgmt/courses'
    success_message = 'User created'

    def form_valid(self, form):
        valid = super(UserAdd, self).form_valid(form)
        form.save()
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password')
        user = User.objects.get(username=username)
        authenticate(username=user, password=password)
        login(self.request, user)
        return valid


class CourseList(generic.ListView):
    """
    Overview of all courses where students can still register

    """

    model = Course_Iteration
    template_name = 'course_registration/course_list.html'
    context_object_name = 'course_list'
    success_url = '/course_mgmt/courses'
    paginate_by = 10

    def get_queryset(self):
        """
        Returns all courses with active registration

        :return: course queryset
        """
        new_context = Course_Iteration.objects.filter(course_registration=True)
        return new_context


class CourseDetail(SuccessMessageMixin, generic.DetailView):
    """
    CourseDetail is used to register users for a course
    """
    model = Course
    template_name = 'course_registration/course_detail.html'
    fields = '__all__'
    success_message = 'Registered successfully!'

    def post(self, request, **kwargs):
        """

        :param request:
        :param kwargs:
        :return:
        """

        # get number of required fields
        # if submitted number is equal proceed registration
        course = Course.objects.get(slug=kwargs['slug'])
        count_required_fields = course.required_fields.count()

        # +2 because request.POST contains also the csrf and register token
        if course.course_registration is True and count_required_fields + 2 == len(request.POST) \
                and course.seats_cur < course.seats_max:

            # for every submitted field the field, field value, user and course will
            # be inserted into CourseRegistration
            user = get_user(request)

            for entry in request.POST:
                if entry.startswith('registration_values'):
                    try:
                        field = Field.objects.get(field_name__exact=entry[20:])
                        if field:
                            reg_values = {'user_id': user,
                                          'course_id': course,
                                          'field_id': field,
                                          'field_value': request.POST[entry]}

                            User_Course_Registration.objects.get_or_create(**reg_values)

                    except:
                        print(sys.exc_info())

            course_progress = User_Course_Progress.objects.filter(course_id=course).values_list('user_progress_id')

            if course_progress.count() <= 1:
                prog_values = {'user_id': user,
                               'course_id': course,
                               'user_progress_id': course.course_progress,
                               'progress_reached': True}

                User_Course_Progress.objects.get_or_create(**prog_values)
            else:
                for progress in course_progress:
                    prog_values = {'user_id': user,
                                   'course_id': course,
                                   'user_progress_id_id': progress[0],
                                   'progress_reached': True}

                    User_Course_Progress.objects.get_or_create(**prog_values)

        return HttpResponseRedirect('/course_mgmt/my_courses')


class StudentCourses(LoginRequiredMixin, generic.DetailView):
    """
    Overview of registered courses for a given user.

    Displays courses that are still marked as "active".
    """
    model = User_Course_Progress
    template_name = 'course_registration/my_courses.html'
    context_object_name = 'course_list'
    success_url = '/course_mgmt/my_courses'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        """

        :param request: contains user information
        :param args: not used
        :param kwargs: not used
        :return: user object and a list of all active course progress' for all active courses of this user
        """
        user = get_user(request)
        courses = list(User_Course_Progress.objects.lowest_unfinished().filter(user_id=user))

        return render(request, 'course_registration/my_courses.html', {'user': user, 'course_list': courses})


class TeacherCourses(generic.ListView):
    """
    Course list for all courses of a teacher.

    Courses can be activated/deactivated and registration can be opened/closed. Also shows the current/max seats for
    this course and a unique URL that can be given to students.
    """
    model = Course
    template_name = 'course_registration/teacher_courses.html'
    context_object_name = 'course_list'
    success_url = '/course_mgmt/teacher_courses'
    paginate_by = 10

    @method_decorator(user_passes_test(lambda u: u.groups.filter(name='teacher').count() == 1))
    def dispatch(self, *args, **kwargs):
        return super(TeacherCourses, self).dispatch(*args, **kwargs)

    def get_queryset(self):

        """
        Returns a list of courses for the given teacher.

        List is sorted first by active/inactive and then by course name.

        :return: Course queryset with all courses of the teacher
        """
        teacher = get_user(self.request)
        new_context = Course.objects.filter(course_teacher=teacher).order_by('-course_active', 'course_name')
        return new_context

    def post(self, request):
        """
        The user can toggle the status for "course_active" and "course_registration" to disable
        the registration for a course in progress or also the whole course.

        :param request: used to get the IDs of courses that should be toggled
        :return: refreshes the page with updated courses
        """

        if 'course_registration_id' in request.POST:
            positive_ids, negative_ids = subtract_ids(request, 'course_registration_id')

            Course.objects.filter(id__in=positive_ids).update(course_registration=True)
            Course.objects.filter(id__in=negative_ids).update(course_registration=False)

        if 'course_active_id' in request.POST:
            positive_ids, negative_ids = subtract_ids(request, 'course_active_id')

            Course.objects.filter(id__in=positive_ids).update(course_active=True)
            Course.objects.filter(id__in=negative_ids).update(course_active=False)

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
        """

        creates new course with attributes att, default values are used for:
        course_active = models.BooleanField(default=True)
        course_registration = models.BooleanField(default=True)
        slug = models.SlugField(max_length=200, blank=True)
        slug field is generated in save method of model "Course"

        :param request:
        :param kwargs:
        :return:
        """

        att = {'course_name': request.POST['course_name'],
               'course_teacher': get_user(request),
               'course_progress': Progress.objects.get(id=request.POST['course_progress']),
               'seats_max': request.POST['seats_max']}

        course = Course.objects.create(**att)

        # adds many-to-many entries for all required fields
        course.required_fields.add(*request.POST.getlist('required_fields'))

        return HttpResponseRedirect('/course_mgmt/teacher_courses')


class TeacherCoursesDetail(SuccessMessageMixin, generic.UpdateView):
    model = Course
    template_name = 'course_registration/teacher_courses_detail.html'
    form_class = CourseProgressUpdateForm

    def get(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs: finds the course via its course slug (URL)
        :return:
        """
        course = Course.objects.get(slug=kwargs['slug'])
        form = CourseProgressUpdateForm(data={'course_progress': course.course_progress_id})
        fields = course.required_fields.all()

        # gets all required fields for this course
        # right now there is no positional argument for the fields, so more important fields need
        # to be added to the database earlier
        course_details = User_Course_Registration.objects.filter(course_id=course.id).order_by('field_id')

        # finds unfinished course progress with lowest id for every user
        course_progress = list(User_Course_Progress.objects.lowest_unfinished().filter(course_id=course.id))


        # creates student_dict to capture all fields/values for a user
        student_dict = OrderedDict()
        for entry in course_details:
            if entry.user_id_id not in student_dict:
                student_dict[entry.user_id_id] = OrderedDict()
            student_dict[entry.user_id_id][entry.field_id_id] = entry.field_value

        # adds the last progress of this student to the list
        for progress in course_progress:
            if progress.user_id_id in student_dict:
                student_dict[progress.user_id_id]['progress'] = progress.user_progress_id.progress_name
                student_dict[progress.user_id_id]['progress_reached'] = progress.progress_reached

        # splits the student_dict in two different dicts for easier processing in the template
        student_complete_dict = OrderedDict()
        student_incomplete_dict = OrderedDict()

        for student in student_dict.items():
            if course.course_progress.progress_name == student[1]['progress']:
                student_complete_dict[student[0]] = student[1]
            else:
                student_incomplete_dict[student[0]] = student[1]

        return render(request, 'course_registration/teacher_courses_detail.html',
                      {'form': form, 'course': course, 'student_complete_list': student_complete_dict,
                       'student_incomplete_list': student_incomplete_dict, 'field_list': fields})

    def post(self, request, *args, **kwargs):

        course = Course.objects.get(slug=kwargs['slug'])

        if 'update_course_progress' in request.POST:
            # write new course progress
            new_progress = Progress.objects.get(id=request.POST['course_progress'])
            course.course_progress = new_progress
            course.save()

            # write new student progress entry for all students
            student_list = User_Course_Progress.objects.filter(course_id=course.id).order_by('user_id')
            last_student = None
            for student in student_list:
                if student.user_id != last_student:
                    last_student = student.user_id
                    att = {'user_id': student.user_id,
                           'course_id': course,
                           'user_progress_id': new_progress}
                    User_Course_Progress.objects.get_or_create(**att)

            return HttpResponseRedirect('/course_mgmt/teacher_courses_detail/' + kwargs['slug'])

        elif 'update_student_progress' in request.POST:
            course_progress = User_Course_Progress.objects.lowest_unfinished().filter(course_id=course.id)

            positive_ids, negative_ids = subtract_ids(request, 'student_id')

            course_progress.filter(user_id__in=positive_ids).update(progress_reached=True)
            course_progress.filter(user_id__in=negative_ids).update(progress_reached=False)

            return HttpResponseRedirect('/course_mgmt/teacher_courses_detail/' + kwargs['slug'])

        elif 'export' in request.POST:
            fields = course.required_fields.all()
            course_details = User_Course_Registration.objects.filter(course_id=course.id).distinct().values()
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

    def get(self, request, **kwargs):
        """

        :param request:
        :param kwargs:
        :return:
        """
        user = User.objects.get(id=kwargs['user'])
        request_user = get_user(request)
        course = Course.objects.get(slug=kwargs['slug'])
        progress_list = User_Course_Progress.objects.filter(user_id=user, course_id=course)

        is_user = False
        is_teacher = False

        if request_user == user:
            is_user = True

        if course.course_teacher == request_user:
            is_teacher = True

        return render(request, 'course_registration/student_courses_detail.html',
                      {'progress_list': progress_list, 'course_user': user, 'course': course,
                       'is_user': is_user, 'is_teacher': is_teacher})

    def post(self, request, *args, **kwargs):
        positive_ids, negative_ids = subtract_ids(request, 'progress_id')

        User_Course_Progress.objects.filter(id__in=positive_ids).update(progress_reached=True)
        User_Course_Progress.objects.filter(id__in=negative_ids).update(progress_reached=False)

        return HttpResponseRedirect('/course_mgmt/teacher_courses_detail/' + kwargs['slug'])
