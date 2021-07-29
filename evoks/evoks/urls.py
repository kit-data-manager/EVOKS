from django.urls import include, path
from . import views

"""evoks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name='base.html')),
    path('vocabularies/', include('vocabularies.urls')),
    
    path('logout', views.logout_view, name='logout'),
    path('signup', views.signup_view, name='signup'),
    path('login', views.login_view, name='login'),
    path('reset', TemplateView.as_view(template_name='reset_password.html'), name='password_reset'),
    path('profile', TemplateView.as_view(template_name='profile.html'), name='profile'),

    path('teams', TemplateView.as_view(template_name='teams.html'), name='teams'),
    path('teams/<slug:name>', TemplateView.as_view(template_name='team_detail.html')),

    path('help', TemplateView.as_view(template_name='help_page.html'), name='help'),

    path('main', TemplateView.as_view(template_name='base.html'), name='dashboard')
    

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
