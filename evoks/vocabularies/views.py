from django import template
from django.http.request import HttpRequest
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.template import loader
from SPARQLWrapper import SPARQLWrapper, JSON
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect, reverse
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied

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
        if('delete' in request.POST):
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
    # if request.user.is_authenticated:
    #user = request.user
    vocabulary = Vocabulary.objects.get(name=name)
    profiles = vocabulary.profiles.all()
    p = Paginator(profiles, 10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)

    #TODO
    #allow empty list?
    #does it show all users of group or just groups?

    p.allow_empty_first_page
 
    context = {
        'vocabulary' : vocabulary,
        'members' : page_obj
    }

    if(request.method == 'POST'):
        if('invite' in request.POST):
            #still to sensitive should ignore things like whitespace at the end

            #needs permission owner?
            #if user.has_perm('owner', vocabulary):
            invite_str = request.POST['email']
            #add immediately or send invite email?
            #right error codes?

            #check if User/Group exists
            if User.objects.filter(email=invite_str).exists():
                invite_user = User.objects.get(email=invite_str)
                #check if User already on vocabulary
                if not vocabulary.profiles.all().filter(user=invite_user).exists():
                    vocabulary.add_profile(invite_user.profile, 'participant')
                else:
                    return HttpResponse('User is already part of this vocabulary', status=400)
            elif Group.objects.filter(name=invite_str).exists():
                invite_group = Group.objects.get(name=invite_str)
                #check if Group already on vocabulary
                if not vocabulary.groups.all().filter(group=invite_group).exists():
                    vocabulary.add_group(invite_group.groupprofile, 'participant')
                else:
                     return HttpResponse('Group is already part of this vocabulary', status=400)
            else:
                return HttpResponse('User/Group does not exist', status=404)
            #refresh page
            return redirect('vocabulary_members', vocabulary.name)
            #else
                #raise PermissionDenied
        elif('kickall' in request.POST):
            #needs permission owner?
            #if user.has_perm('owner', vocabulary):
            for p in vocabulary.profiles.all():
                #kick creator too?
                vocabulary.remove_profile(p)
            return redirect('vocabulary_members', vocabulary.name)
            #else
                #raise PermissionDenied

        #for loop ok?
        for p in vocabulary.profiles.all():
            #needs permission owner?
            #if user.has_perm('owner', vocabulary):
            if('kick {0}'.format(p.name) in request.POST):
                vocabulary.remove_profile(p)
                return redirect('vocabulary_members', vocabulary.name)

            #else
                #raise PermissionDenied

    return render(request, 'vocabulary_members.html', context)