from django import template
from django.urls import include, path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('<slug:voc_name>', views.index, name='vocabulary_overview'),
    path('<slug:voc_name>/terms', views.terms, name='vocabulary_terms'),
    path('<slug:voc_name>/members', views.members, name='vocabulary_members'),
    path('<slug:voc_name>/prefixes', views.prefixes, name='vocabulary_prefixes'),
    path('<slug:voc_name>/settings', views.settings, name='vocabulary_settings'),
    path('<slug:voc_name>/terms/', include('Term.urls')),
]
