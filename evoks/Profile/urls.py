from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.profile_view, name='profile')
    
]
    
