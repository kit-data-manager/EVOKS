from django import template
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.template import loader
from SPARQLWrapper import SPARQLWrapper, JSON
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


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

def vocabulary_list_view(request):
    if request.user.is_authenticated:      
        user=request.user
        pagesize=10
        vocabularies = Vocabulary.objects.all()
        vocabularies_paged=Paginator(vocabularies,pagesize)
        page = request.POST.get('page')
        #tests if page number is within the range
        try:        
            posts = vocabularies_paged.page(page) 
        except PageNotAnInteger: 
            posts = vocabularies_paged.page(1) 
        except EmptyPage:
             posts = vocabularies_paged.page(vocabularies_paged.num_pages)

        return render(request=request,
                      template_name="base.html",
                      context={'vocabularies':vocabularies_paged,'vocabularies_page':posts})

    return redirect('/login')
    # redirect to login page if user is not authenticated


    