from django.urls import include, path
from . import views

urlpatterns = [
    path('<slug:term_name>', views.term_detail, name='term_detail'),
]