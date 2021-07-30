import datetime
from django import template
from django.db.models import query
from django.db.models.query_utils import Q
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
import xml.dom.minidom
import json
from Comment.models import Comment
from itertools import chain
from guardian.shortcuts import get_perms


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


def convert_predicate(namespaces, predicate):

    return ''


def index(request, name):

    if request.user.is_authenticated:
        user = request.user
        vocabulary = Vocabulary.objects.get(name=name)
        user_is_owner = 'owner' in get_perms(user, vocabulary)
        user_is_participant = 'participant' in get_perms(user, vocabulary)
        user_is_spectator = 'spectator' in get_perms(user, vocabulary)
        user_is_staff = user.is_staff

        # check if user is allowed to view vocabulary
        if user_is_owner or user_is_participant or user_is_spectator or user_is_staff or vocabulary.state == 'Review':
            # put comments and tags on vocabulary into a list sorted from newest to oldest
            comments = vocabulary.comment_set.filter()
            tags = vocabulary.tag_set.filter()
            activity_list = sorted(
                chain(comments, tags),
                key=lambda obj: str(obj.post_date), reverse=True)
            for index, key in enumerate(activity_list):
                activity_list[index].type = key.__class__.__name__

            context = {
                'user': request.user,
                'vocabulary': vocabulary,
                'activities': activity_list
            }

            if request.method == 'POST':

                # create comment
                if 'comment' in request.POST:
                    comment_text = request.POST['comment-text']
                    Comment.create(
                        text=comment_text, author=user.profile, vocabulary=vocabulary, term=None)
                    # refresh page so created comment is visible
                    return redirect('vocabulary_overview', name=name)

                # create tag
                elif 'tag' in request.POST:
                    tag_name = request.POST['tag-name']
                    tag = Tag.create(
                        name=tag_name, author=user.profile, vocabulary=vocabulary, term=None)
                    # refresh page so created tag is visible
                    return redirect('vocabulary_overview', name=name)

                elif 'delete-tag' in request.POST:
                    print(request.POST['delete-tag'])
                    tag = Tag.objects.get(name=request.POST['delete-tag'])
                    tag.delete()

                elif 'create-property' in request.POST:
                    p = fuseki_dev.query(
                        vocabulary, """DESCRIBE <http://www.yso.fi/onto/yso/>""", 'xml')

                    namespaces = []
                    for short, uri in p.namespaces():
                        namespaces.append((short, uri.toPython()))

                    predicate = request.POST['predicate']
                    type = request.POST['type']
                    object_string = request.POST['object']
                    if type == 'uri':
                        object = '<{0}>'.format(object_string)
                    else:
                        object = '{0}'.format(object_string)
                    urispace = '<{0}>'.format(vocabulary.urispace)
                    prefix_list = []
                    for key, value in namespaces:
                        prefix_string = 'prefix {0}: <{1}>'.format(key, value)
                        prefix_list.append(prefix_string)
                    query = """"""
                    for x in prefix_list:
                        query += '{0} \n'.format(x)




                    query += """
                        INSERT DATA {{ {0} {1} {2} }}
                    """.format('<http://www.yso.fi/onto/yso/>', predicate, object)
                    print('Query String: {0}'.format(query))
                    thing = 123
                    #thing = fuseki_dev.query(vocabulary=vocabulary, query=query, return_format='json')
                    print('Query: {0}'.format(thing))
                    print('{0} {1} {2}'.format(predicate, type, object))

                #TODO put in right view, change create_team modal form action
                elif 'create-team' in request.POST:
                    team_name = request.POST['team-name']
                    Group.objects.create(name=team_name)
                    print(Group.objects.get(name=team_name))
        else:
            return HttpResponse('your not part of this vocabulary')

        thing = fuseki_dev.query(vocabulary, """
            SELECT * WHERE {
                <http://www.yso.fi/onto/yso/> ?pred ?obj .
            }
        """, 'json')

        p = fuseki_dev.query(
            vocabulary, """DESCRIBE <http://www.yso.fi/onto/yso/>""", 'xml')

        namespaces = []
        for short, uri in p.namespaces():
            namespaces.append((short, uri.toPython()))
            #print(uri.toPython())

        #print('--------------------')
        fields = {}
        for x in thing['results']['bindings']:
            pred = x['pred']['value']
            obj = x['obj']
            if pred not in fields:
                # print(pred)
                type = pred.rsplit('#', 1)[-1]
                if type == pred:
                    type = pred.rsplit('/', 1)[-1]

                max = 0
                max_prefix = ''
                count = 0
                for s, p in namespaces:
                    for i, e in enumerate(p):
                        if len(pred) > i and e == pred[i]:
                            count += 1
                        else:
                            continue
                    if count > max:
                        max = count
                        max_prefix = (s, p)
                    count = 0

                # print(max_prefix)
                shortcut = '{prefix}:{type}'.format(
                    prefix=max_prefix[0], type=type)
                fields[pred] = {
                    'type': shortcut, 'objects': [obj]}
            else:
                fields[pred]['objects'].append(obj)

        #print(json.dumps(fields, indent=4, sort_keys=True))
        #dom = xml.dom.minidom.parseString(thing)
        #pretty_xml_as_string = dom.toprettyxml()
        # print(pretty_xml_as_string)
        # print(thing.serialize(format='n3'))
        # for s, p, o in thing:
        #    print(p, o)
        template = loader.get_template('vocabulary.html')
        context = {
            'user': request.user,
            'vocabulary': vocabulary,
            'fields': fields,
            'activities': activity_list
        }
        return HttpResponse(template.render(context, request))
        # return HttpResponse('pls login')
    else:
        return redirect('login')


def settings(request, name):
    if request.user.is_authenticated:
        try:
            vocabulary = Vocabulary.objects.get(name=name)
            print(vocabulary.state)
        except ObjectDoesNotExist:
            return redirect('base')

        user = request.user
        user_is_owner = 'owner' in get_perms(user, vocabulary)
        user_is_staff = user.is_staff

        context = {
            'vocabulary': vocabulary
        }

        if request.method == 'POST':
            if user_is_owner or user_is_staff:
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
    else:
        return redirect('login')


def members(request: HttpRequest, name):
    if request.user.is_authenticated:
        user = request.user
        vocabulary = Vocabulary.objects.get(name=name)

        profiles_list = vocabulary.profiles.all()
        user_list = []
        for key in profiles_list:
            user_list.append(key.user)
        groups = vocabulary.groups.all()
        group_user_list = []
        for key in groups:
            group_user_list.extend(key.group.user_set.all())
        member_list = set()
        for key in user_list:
            member_list.add(key)
        for key in group_user_list:
            member_list.add(key)
        member_list = list(member_list)
        #member_list = list(chain(user_list, group_user_list))
        print('This member list: {0}'.format(member_list))

        p = Paginator(member_list, 10)
        page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)

        user_is_owner = 'owner' in get_perms(user, vocabulary)
        user_is_staff = user.is_staff

        # TODO
        # allow empty list?
        # does it show all users of group or just groups?

        p.allow_empty_first_page

        context = {
            'vocabulary': vocabulary,
            'members': page_obj
        }

        if request.method == 'POST':
            if user_is_owner or user_is_staff:

                if 'invite' in request.POST:
                    # still too sensitive should ignore things like whitespace at the end

                    invite_str = request.POST['email']
                    # add immediately or send invite email?
                    # right error codes?

                    # check if User/Group exists
                    if User.objects.filter(email=invite_str).exists():
                        invite_user = User.objects.get(email=invite_str)
                        # check if User already on vocabulary
                        if not vocabulary.profiles.all().filter(user=invite_user).exists():
                            vocabulary.add_profile(
                                invite_user.profile, 'participant')
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
                elif 'kickall' in request.POST:
                    for p in vocabulary.profiles.all():
                        # kick creator too?
                        vocabulary.remove_profile(p)
                    return redirect('vocabulary_members', vocabulary.name)

                # for loop ok?
                for p in vocabulary.profiles.all():
                    if('kick {0}'.format(p.name) in request.POST):
                        vocabulary.remove_profile(p)
                        return redirect('vocabulary_members', vocabulary.name)

            else:
                raise PermissionDenied

        return render(request, 'vocabulary_members.html', context)
    else:
        return redirect('login')


def terms(request: HttpRequest, name: str):
    vocabulary = Vocabulary.objects.get(name=name)

    letter = request.GET.get('letter') or 'a'
    page_number = int(request.GET.get('page') or 1)

    limit = 20
    offset = (page_number-1) * limit

    form = Vocabulary_Terms_Form(
        initial={'initial_letter': (letter, letter.upper())})

    query = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT DISTINCT ?sub ?pred ?obj
    WHERE {{
        ?sub skos:prefLabel ?obj .
    FILTER (strstarts(str(?obj), '{letter}'))
    FILTER (lang(?obj) = 'en')
    }}
    ORDER BY ?obj
    LIMIT {limit} OFFSET {offset}
    """.format(limit=20, offset=offset, letter=letter)

    thing = fuseki_dev.query(vocabulary, query, 'json')

    terms = []
    for x in thing['results']['bindings']:
        obj = x['obj']
        terms.append({'name': obj['value']})

    # print(json.dumps(thing, indent=4, sort_keys=True))

    #initial_terms = terms.filter(name__startswith=initial_letter)
    #p = Paginator(terms, 10)
    #page_number = request.GET.get('page')
    #page_obj = p.get_page(page_number)

    # p.allow_empty_first_page

    # TODO filter queryset by initial letter, sort queryset alphabeticaly
    # form.add_initial_prefix(letter)
    context = {
        'vocabulary': vocabulary,
        'terms': {'data': terms, 'next_page_number': page_number+1, 'previous_page_number': 1 if page_number-1 == 0 else page_number-1, 'start_index': offset, 'end_index': offset+len(terms)},
        'initial_letter': form,
    }
    return render(request, 'vocabulary_terms.html', context)

def base(request : HttpRequest):
    user = request.user
    if request.method == 'POST':

        if 'create-vocabulary' in request.POST:
                        if 'file-upload' in request.FILES:
                            import_voc = request.FILES['file-upload']
                            Vocabulary.import_vocabulary(import_voc)
                        elif request.POST['name'] != '' and request.POST['urispace'] != '':
                            try:
                                voc_name = request.POST['name']
                                urispace = request.POST['urispace']
                                Vocabulary.create(
                                    name=voc_name, urispace=urispace, creator=user.profile)
                            except IntegrityError:
                                return HttpResponse('vocabulary already exists')
    return render(request, 'base.html')
