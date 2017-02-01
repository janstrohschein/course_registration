from django.contrib import admin
from .models import *

# Register your models here.
#admin.site.register(User)
admin.site.register(User_Course_Registration)
admin.site.register(User_Course_Progress)
admin.site.register(Field)
admin.site.register(Progress)
admin.site.register(Course_Iteration)

class CourseAdmin(admin.ModelAdmin):
    def save_related(self, request, form, *args, **kwargs):
        super(CourseAdmin, self).save_related(request, form, *args, **kwargs)
        obj = form.instance
        fk = Field.objects.get(field_name__exact='Email')
        obj.required_fields.add(fk)

admin.site.register(Course, CourseAdmin)