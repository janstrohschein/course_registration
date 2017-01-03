from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(User_Course_Registration)
admin.site.register(User_Course_Progress)
admin.site.register(Field)
admin.site.register(Course)
admin.site.register(Progress)
