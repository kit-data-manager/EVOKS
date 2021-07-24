from django import template
from django.http.request import HttpRequest
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.template import loader
from SPARQLWrapper import SPARQLWrapper, JSON
from django.contrib.auth.models import User
from django.shortcuts import redirect

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
    vocabulary = Vocabulary.objects.get(name=name)
    #vocabulary = Vocabulary.objects.create(name='abc')
    context = {
        'vocabulary': vocabulary
    }
    if(request.method == 'POST'):
        if('overview' in request.POST):
            return redirect('vocabulary_overview', name=vocabulary.name)
        elif('terms' in request.POST):
            return redirect('vocabulary_terms', name=vocabulary.name)
        elif('members' in request.POST):
            return redirect('vocabulary_members', name=vocabulary.name)
        elif('settings' in request.POST):
            return redirect('vocabulary_settings', name=vocabulary.name)
        elif('delete' in request.POST):
            #vocabulary.delete()
            return redirect('profile')
        elif(request.POST['vocabulary-setting'] == 'Live'):
            vocabulary.set_live()
        elif(request.POST['vocabulary-setting'] == 'Development'):
            vocabulary.set_review()
        elif(request.POST['vocabulary-setting'] == 'Private to you'):
            vocabulary.set_dev()
        
    return render(request, 'vocabulary_setting.html', context)


def members(request : HttpRequest, name):
    vocabulary = Vocabulary.objects.get(name=name)
    
    user = User.objects.create(username='jhon', password='ok',
                            email='someone@example.com')
    #vocabulary = Vocabulary.create(name)
    #context ={}
 
    # add the dictionary during initialization
    context = {
        'vocabulary' : vocabulary,
        'members' : vocabulary.profiles
    }
    if(request.method == 'POST'):
        if(request.POST['kick'] == 'abc'):
            vocabulary.remove_profile(vocabulary.profiles.get(username='abc'))

    return render(request, 'vocabulary_members.html', context)