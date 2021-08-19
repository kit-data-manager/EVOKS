from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.teams_view, name='team_list'),
    path('/<group_name>', views.team_detail_view, name='teams')
]