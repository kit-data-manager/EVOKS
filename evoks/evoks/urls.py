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

    # path('vocabularies', TemplateView.as_view(template_name='base.html')),

    path('vocabularies', include('vocabularies.urls')),
    
    path('signup', TemplateView.as_view(template_name='signup.html')),
    path('login', TemplateView.as_view(template_name='login.html')),
    path('reset', TemplateView.as_view(template_name='reset_password.html')),
    path('profile', include('Profile.urls')),
    path('teams', include('GroupProfile.urls')),
    path('help', TemplateView.as_view(template_name='help_page.html')),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
