from django import template
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('/<slug:name>', views.index, name='vocabulary_overview'),
    path('/<slug:name>/terms', views.terms, name='vocabulary_terms'),
    path('/<slug:name>/members', views.members, name='vocabulary_members'),
    path('/<slug:name>/prefixes', views.prefixes, name='vocabulary_prefixes'),
    path('/<slug:name>/settings', views.settings, name='vocabulary_settings'),
    path('/<slug:name>/term_detail',
         TemplateView.as_view(template_name='term_detail.html'), name='term_detail'),
]
