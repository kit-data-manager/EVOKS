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
    #user = User.objects.create(username='jebediah', password='ok', email='jebediah@example.com')
    vocabulary = Vocabulary.objects.get(name=name)
    #user = User.objects.get(username='jhon')
    #vocabulary = Vocabulary.create(name='TestVoc', creator=user.profile)
    #vocabulary = Vocabulary.create(name)
    #context ={}
 
    # add the dictionary during initialization
    context = {
        'vocabulary' : vocabulary,
        'members' : vocabulary.profiles.all(),
        'page' : 1
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
        elif('invite' in request.POST):
            #needs permission owner?
            email = request.POST['email']
            #needs to check if user exists
            invite_user = User.objects.get(email=email)
            vocabulary.add_profile(invite_user.profile, 'participant')
        elif('kickall' in request.POST):
            #needs permission owner?
            for p in vocabulary.profiles.all():
                #kick creator too?
                vocabulary.remove_profile(p)
        #for loop ok?
        for p in vocabulary.profiles.all():
            #needs permission owner?
            if('kick {0}'.format(p.name) in request.POST):
                vocabulary.remove_profile(p)

    return render(request, 'vocabulary_members.html', context)