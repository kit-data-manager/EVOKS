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
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from rdflib import Graph, Literal
import time
from typing import List
from django.db import IntegrityError

from django.core.exceptions import PermissionDenied
from .forms import Vocabulary_Terms_Form
from Term.models import Term
from Tag.models import Tag
from evoks.fuseki import fuseki_dev
from evoks.forms import CreateVocabularyForm


def convert_prefixes(prefixes: List[str]):
    converted: List[str]
    for prefix in prefixes:
        parts = prefix.split()
        converted.append('PREFIX {prefix} {url}'.format(
            prefix=parts[1], url=parts[2]))

    return converted


def prefixes(request, name):
    vocabulary = Vocabulary.objects.get(name=name)

    if request.method == 'POST':
        prefixes = request.POST['prefixes'].split(
            '\r\n')  # could lead to problems with \r\n
        non_empty_prefixes = [line for line in prefixes if line.strip() != ""]
        vocabulary.prefixes = non_empty_prefixes
        convert_prefixes(non_empty_prefixes)
        vocabulary.save()

    template = loader.get_template('vocabulary_prefixes.html')
    context = {
        'user': request.user,
        'vocabulary': vocabulary,
        'prefixes': '\n'.join(vocabulary.prefixes),
    }

    return HttpResponse(template.render(context, request))


def index(request, name):
    if request.user.is_authenticated:
        vocabulary = Vocabulary.objects.get(name=name)
        if request.method == 'POST':
            if request.POST['tag-name'] != '':
                tag_name = request.POST['tag-name']
                print(tag_name)
                tag = Tag.create(name=tag_name, vocabulary=vocabulary)
                print('Color of the Created Tag: {0}'.format(tag.color))
                return redirect('vocabulary_overview', name=name)
            form = CreateVocabularyForm(request.POST, request.FILES)
            if form.is_valid():
                if request.FILES['file-upload'] != None:
                    import_voc = request.FILES['file-upload']
                    Vocabulary.import_vocabulary(import_voc)
                elif request.POST['name'] != '' and request.POST['urispace'] != '':
                    try:
                        voc_name = form.cleaned_data['name']
                        urispace = form.cleaned_data['urispace']
                        Vocabulary.create(name=voc_name, urispace=urispace, creator=request.user.profile)
                        print('created smthn vocabulary yaa')
                    except IntegrityError:
                        return HttpResponse('vocabulary already exists')
        else:
            form= CreateVocabularyForm()
        # TODO fix csrf
        if request.method == 'DELETE':
            # Delete vocabularyy
            print('DELETETETET')
            # Vocabulary.objects.get(name=name).delete()
            return HttpResponse(status=204)
        print('yeet')
        # if request.user.is_authenticated:
        

        thing = '123'
        thing = fuseki_dev.query(vocabulary, """DESCRIBE <http://www.yso.fi/onto/yso/>""")
        print(thing.serialize(format='n3'))
        for s, p, o in thing:
            print(p, o)
        template = loader.get_template('vocabulary.html')
        context = {
            'user': request.user,
            'vocabulary': vocabulary,
        }
        return HttpResponse(template.render(context, request))
        # return HttpResponse('pls login')
    else:
        return redirect('login')


def settings(request, name):
    try:
        vocabulary = Vocabulary.objects.get(name=name)
        print(vocabulary.state)
    except ObjectDoesNotExist:
        return redirect('base')

    context = {
        'vocabulary': vocabulary
    }

    if request.method == 'POST':
        if 'delete' in request.POST:
            # vocabulary.delete()
            print('yetetet')
            return redirect('base')
        elif(request.POST['vocabulary-setting'] == 'Live'):
            vocabulary.set_live()
        elif(request.POST['vocabulary-setting'] == 'Review'):
            vocabulary.set_review()
        elif(request.POST['vocabulary-setting'] == 'Development'):
            vocabulary.set_dev()
    return render(request, 'vocabulary_setting.html', context)


def members(request: HttpRequest, name):
    # if request.user.is_authenticated:
    #user = request.user
    vocabulary = Vocabulary.objects.get(name=name)
    profiles = vocabulary.profiles.all()
    p = Paginator(profiles, 10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)

    # TODO
    # allow empty list?
    # does it show all users of group or just groups?

    p.allow_empty_first_page

    context = {
        'vocabulary': vocabulary,
        'members': page_obj
    }

    if request.method == 'POST':
        if 'invite' in request.POST:
            # still to sensitive should ignore things like whitespace at the end

            # needs permission owner?
            # if user.has_perm('owner', vocabulary):
            invite_str = request.POST['email']
            # add immediately or send invite email?
            # right error codes?

            # check if User/Group exists
            if User.objects.filter(email=invite_str).exists():
                invite_user = User.objects.get(email=invite_str)
                # check if User already on vocabulary
                if not vocabulary.profiles.all().filter(user=invite_user).exists():
                    vocabulary.add_profile(invite_user.profile, 'participant')
                else:
                    return HttpResponse('User is already part of this vocabulary', status=400)
            elif Group.objects.filter(name=invite_str).exists():
                invite_group = Group.objects.get(name=invite_str)
                # check if Group already on vocabulary
                if not vocabulary.groups.all().filter(group=invite_group).exists():
                    vocabulary.add_group(
                        invite_group.groupprofile, 'participant')
                else:
                    return HttpResponse('Group is already part of this vocabulary', status=400)
            else:
                return HttpResponse('User/Group does not exist', status=404)
            # refresh page
            return redirect('vocabulary_members', vocabulary.name)
            # else
            #raise PermissionDenied
        elif 'kickall' in request.POST:
            # needs permission owner?
            # if user.has_perm('owner', vocabulary):
            for p in vocabulary.profiles.all():
                # kick creator too?
                vocabulary.remove_profile(p)
            return redirect('vocabulary_members', vocabulary.name)
            # else
            #raise PermissionDenied

        # for loop ok?
        for p in vocabulary.profiles.all():
            # needs permission owner?
            # if user.has_perm('owner', vocabulary):
            if('kick {0}'.format(p.name) in request.POST):
                vocabulary.remove_profile(p)
                return redirect('vocabulary_members', vocabulary.name)

            # else
                #raise PermissionDenied

    return render(request, 'vocabulary_members.html', context)


def terms(request: HttpRequest, name: str):
    vocabulary = Vocabulary.objects.get(name=name)
    terms = vocabulary.term_set.all()
    # TODO
    initial_letter = 'a'
    if 'location' in request.POST:
        form = Vocabulary_Terms_Form(request.POST)
        initial_letter = request.POST['location']
    else:
        form = Vocabulary_Terms_Form()

    initial_terms = terms.filter(name__startswith=initial_letter)
    p = Paginator(terms, 10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)

    p.allow_empty_first_page

    # TODO filter queryset by initial letter, sort queryset alphabeticaly

    context = {
        'vocabulary': vocabulary,
        'terms': page_obj,
        'initial_letter': form
    }
    return render(request, 'vocabulary_terms.html', context)
