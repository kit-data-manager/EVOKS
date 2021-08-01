from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.vocabulary_list_view),
    path('/<slug:name>', views.index),
    path('/<slug:name>/terms', TemplateView.as_view(template_name='vocabulary_terms.html')),
    path('/<slug:name>/members', TemplateView.as_view(template_name='vocabulary_members.html')),
    path('/<slug:name>/settings', views.settings),
    path('/<slug:name>/term_detail', TemplateView.as_view(template_name='term_detail.html')),
]