"""course_reg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import views as auth_views
from course_registration import views

urlpatterns = [
    url(r'^$', lambda r: HttpResponseRedirect('course_mgmt/courses')),
    url(r'^course_mgmt/', include('course_registration.urls')),
    url(r'^reset_password/', include('password_reset.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^register$', views.UserAdd.as_view() , {'template_name': 'register.html'},
        name='register'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'},
        name='login'),
    url(r'^logout/$', auth_views.logout,
        {'next_page': 'course_list'}, name='logout'),
]
