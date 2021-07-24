from django import template
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.template import loader
from SPARQLWrapper import SPARQLWrapper, JSON


def index(request, name):

    # TODO fix csrf
    if request.method == 'DELETE':
        # Delete vocabulary
        Vocabulary.objects.get(name=name).delete()
        return HttpResponse(status=204)

    print('yeet')
    # if request.user.is_authenticated:
    vocabulary = Vocabulary.objects.get(name=name)
    print(vocabulary)
    template = loader.get_template('vocabulary.html')
    context = {
        'user': request.user,
        'vocabulary': vocabulary,
    }
    return HttpResponse(template.render(context, request))
    # return HttpResponse('pls login')


def settings(request, name):
    # vocabulary = Vocabulary.objects.get(name=name)
    context = {
        'vocabulary': {'state': 'LIVE'}
    }
    template = loader.get_template('vocabulary_setting.html')
    return HttpResponse(template.render(context, request))
