from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.teams_view),
    path('/<slug:name>', views.team_detail_view,name='teams')
]