from enum import unique
from django.http.request import HttpRequest
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.template import loader
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from typing import List, Tuple
from django.db import IntegrityError
from urllib.parse import urlparse

from evoks.settings import SKOSMOS_LIVE_URI, SKOSMOS_DEV_URI
from django.core.exceptions import PermissionDenied
from .forms import Vocabulary_Terms_Form
from Tag.models import Tag
from evoks.fuseki import fuseki_dev
from Comment.models import Comment
from itertools import chain
from guardian.shortcuts import get_perms
from django.contrib.auth.decorators import login_required, user_passes_test


def prefixes(request: HttpRequest, voc_name: str) -> HttpResponse:
    """Views for prefixes tab

    Args:
        request (HttpRequest): request object
        name (HttpResponse): name of vocabulary

    Returns:
        HttpResponse: HttpResponse
    """
    vocabulary = Vocabulary.objects.get(name=voc_name)

    if request.method == 'POST':
        prefixes = request.POST['prefixes'].split(
            '\r\n')  # could lead to problems with \r\n
        # remove all empty lines
        non_empty_prefixes = [line for line in prefixes if line.strip() != ""]
        vocabulary.prefixes = non_empty_prefixes  # save prefixes in vocabulary
        vocabulary.save()

    template = loader.get_template('vocabulary_prefixes.html')
    context = {
        'user': request.user,
        'vocabulary': vocabulary,
        'prefixes': '\n'.join(vocabulary.prefixes),
    }

    return HttpResponse(template.render(context, request))


def convert_predicate(namespaces: List[Tuple[str, str]], predicate: str) -> str:
    """Convert a URI predicate to a shortened predicate with namespaces

    Args:
        namespaces (List[(str, str)]): List of namespace tuples (prefix, url)
        predicate (str): predicate to be shortened

    Returns:
        str: shortened predicate
    """
    # get type of predicate
    type = predicate.rsplit('#', 1)[-1]
    if type == predicate:
        type = predicate.rsplit('/', 1)[-1]

    # algorithm to find the longest prefix that is a perfect match
    max = 0
    max_prefix = None
    count = 0
    # iterate over namespaces
    for s, p in namespaces:
        # iterate over letters in predicate
        for i, e in enumerate(p):
            # if not out of range and letters are equal
            if len(predicate) > i and e == predicate[i]:
                count += 1
            else:  # out of range, bad luck:(
                continue
        # new best match and matching on complete length
        if count > max and count == len(p):
            max = count
            max_prefix = (s, p)
        count = 0

    # no prefix found, predicate is just a normal URI
    if max_prefix is None:
        return predicate
    return '{prefix}:{type}'.format(
        prefix=max_prefix[0], type=type)


def uri_validator(uri: str) -> bool:
    """validates a URI
    Args:
        uri (str): uri to be validated

    Returns:
        bool: true if valid, false if not
    """
    try:
        result = urlparse(uri)
        return all([result.scheme, result.netloc])
    except:
        return False



def index(request: HttpRequest, voc_name: str) -> HttpResponse:
    """View for vocabulary overview

    Args:
        request (HttpRequest): request object
        name (str): name of vocabulary

    Returns:
        HttpResponse: Http Response object
    """

    user = request.user
    vocabulary = Vocabulary.objects.get(name=voc_name)
    user_is_owner = 'owner' in get_perms(user, vocabulary)
    user_is_participant = 'participant' in get_perms(user, vocabulary)
    user_is_spectator = 'spectator' in get_perms(user, vocabulary)

    # check if user is allowed to view vocabulary
    if user_is_owner or user_is_participant or user_is_spectator or vocabulary.state == 'Review':

        # put comments and tags on vocabulary into a list sorted from newest to oldest
        comments = vocabulary.comment_set.filter()
        tags = vocabulary.tag_set.filter()
        activity_list = sorted(
            chain(comments, tags),
            key=lambda obj: str(obj.post_date), reverse=True)

        # add type of activity to activity list so we can render it differently
        for index, key in enumerate(activity_list):
            activity_list[index].type = key.__class__.__name__

        if request.method == 'POST':

            if 'obj' in request.POST:
                namespaces = vocabulary.get_namespaces()

                key = request.POST['key']
                obj = request.POST['obj']
                lang = request.POST['lang']
                new_obj = request.POST['new-obj']
                type = request.POST['obj-type']
                query = vocabulary.prefixes_to_str(namespaces)
                # convert prefixes to sparql format

                # if we want to edit a field
                if new_obj != '':
                    if type == 'uri':
                        # if uri is not valid its using a prefix and does not need braces
                        if uri_validator(new_obj) != True:
                            new_object = new_obj
                        else:
                            new_object = '<{0}>'.format(new_obj)
                    else:
                        new_object = '\'{0}\''.format(new_obj)
                        if lang != '':  # add lang tag if it exists
                            new_object += '@{0}'.format(lang)
                # format the old object correctly
                if type == 'uri':
                    # if uri is not valid its using a prefix and does not need braces
                    if uri_validator(new_obj) != True:
                        new_object = new_obj
                    else:
                        new_object = '<{0}>'.format(new_obj)
                else:
                    new_object = '\'{0}\''.format(new_obj)
                    if lang != '':  # add lang tag if it exists
                        new_object += '@{0}'.format(lang)

                # format the old object correctly
                if type == 'uri':
                    if uri_validator(obj) != True:
                        object = obj
                    else:
                        object = '<{0}>'.format(obj)
                else:
                    object = '\'{0}\''.format(obj)
                    if lang != '':
                        object += '@{0}'.format(lang)

                # delete field
                if new_obj == '':
                    query += """
                    DELETE DATA
                    {{ <{urispace}> <{predicate}> {object} }}
                    """.format(urispace=vocabulary.urispace, predicate=key, object=object)
                    fuseki_dev.query(
                        vocabulary, query, 'xml', 'update')
                # edit field
                else:
                    query += """
                    DELETE {{ <{urispace}> <{predicate}> {object} }}
                    INSERT {{ <{urispace}> <{predicate}> {new_object} }}
                    WHERE
                    {{ <{urispace}> <{predicate}> {object} }}
                    """.format(new_object=new_object, urispace=vocabulary.urispace, predicate=key, object=object)
                    fuseki_dev.query(
                        vocabulary, query, 'xml', 'update')
            # create comment
            elif 'comment' in request.POST:
                comment_text = request.POST['comment-text']
                Comment.create(
                    text=comment_text, author=user.profile, vocabulary=vocabulary, term=None)
                # refresh page so created comment is visible
                return redirect('vocabulary_overview', voc_name=vocabulary.name)

            # create tag
            elif 'tag' in request.POST:
                tag_name = request.POST['tag-name']

                # we only want 1 tag with the same name per vocabulary
                Tag.objects.filter(
                    name=tag_name, vocabulary=vocabulary).delete()
                # create new tag
                Tag.create(
                    name=tag_name, author=user.profile, vocabulary=vocabulary, term=None)
                return redirect('vocabulary_overview', voc_name=vocabulary.name)

            elif 'delete-tag' in request.POST:
                tag_name = request.POST['delete-tag']
                Tag.objects.filter(
                    name=tag_name, vocabulary=vocabulary).delete()
                return redirect('vocabulary_overview', voc_name=vocabulary.name)

            elif 'create-property' in request.POST:
                predicate = request.POST['predicate']
                type = request.POST['type']
                object_string = request.POST['object']
                if type == 'uri':
                    # if uri is not valid its using a prefix and does not need braces
                    if uri_validator(object_string) != True:
                        object = object_string
                    else:
                        object = '<{0}>'.format(object_string)
                else:
                    object = '\'{0}\''.format(object_string)
                urispace = '<{0}>'.format(vocabulary.urispace)
                vocabulary.create_field(urispace, predicate, object)

            elif 'download' in request.POST:
                dataformat = request.POST['download']
                result = vocabulary.export_vocabulary(dataformat)
                return result

        # query all fields of the vocabulary
        query_result = fuseki_dev.query(vocabulary, """
            SELECT * WHERE {{
                <{0}> ?pred ?obj .
            }}
        """.format(vocabulary.urispace), 'json')

        namespaces = vocabulary.get_namespaces()

        # manipulate fields to make the templating easier
        fields = {}
        for x in query_result['results']['bindings']:
            pred = x['pred']['value']
            obj = x['obj']
            if pred not in fields:
                # create new predicate shortcut and initialize object list
                shortcut = convert_predicate(namespaces, pred)
                fields[pred] = {
                    'type': shortcut, 'objects': []}

            # if uri, add shortcut if possible
            if obj['type'] == 'uri':
                shortcut = convert_predicate(namespaces, obj['value'])
                obj['shortcut'] = shortcut if shortcut[-1] != ':' else obj['value']

            # add language tag
            if 'xml:lang' in obj:
                obj['lang'] = obj['xml:lang']

            # append object to list of objects with same predicate
            fields[pred]['objects'].append(obj)

        search = request.GET.get('search')
        search_results = None
        if search != None:
            search_results = []

            # query all fields of the vocabulary
            query_result = fuseki_dev.query(vocabulary, """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

                SELECT DISTINCT ?s ?p ?o
                WHERE {{
                    ?s skos:prefLabel ?o .
                FILTER (strstarts(str(?o), '{0}'))
                }}
            """.format(search), 'json')

            for x in query_result['results']['bindings']:
                s = x['s']['value']
                value = x['o']['value']
                id = s.split(vocabulary.urispace)[1]
                search_results.append((id, value))

        template = loader.get_template('vocabulary.html')
        skosmos_url = SKOSMOS_DEV_URI if vocabulary.state == State.REVIEW else SKOSMOS_LIVE_URI
        vocabularyVer = vocabulary.version - 1
        context = {
            'user': request.user,
            'vocabulary': vocabulary,
            'fields': fields,
            'activities': activity_list,
            'search_results': search_results,
            'search_term': search,
            'skosmos_url': skosmos_url + vocabulary.name + '-' + str(vocabularyVer),
        }
        return HttpResponse(template.render(context, request))

    else:
        return HttpResponse('your not part of this vocabulary')


def settings(request: HttpRequest, voc_name: str):
    """View for settings tab on a vocabulary

    Args:
        request (HttpRequest): Current request
        name (str): Name of the vocabulary

    Returns:
        HttpResponse: Rendered Settings Site
    """
    try:
        vocabulary = Vocabulary.objects.get(name=voc_name)
    except ObjectDoesNotExist:
        return redirect('base')

    user = request.user
    user_is_owner = 'owner' in get_perms(user, vocabulary)

    context = {
        'vocabulary': vocabulary
    }

    if request.method == 'POST':
        if user_is_owner:
            # delete vocabulary
            if 'delete' in request.POST:
                if vocabulary.state == State.REVIEW:
                    skosmos_dev.delete_vocabulary(vocabulary.name)
                fuseki_dev.delete_vocabulary(vocabulary)
                vocabulary.delete()
                return redirect('base')

            # change state of vocabulary
            elif(request.POST['vocabulary-setting'] == 'Live'):
                vocabulary.set_live()
            elif(request.POST['vocabulary-setting'] == 'Review'):
                vocabulary.set_review()
            elif(request.POST['vocabulary-setting'] == 'Development'):
                vocabulary.set_dev()

    return render(request, 'vocabulary_setting.html', context)


def members(request: HttpRequest, voc_name: str):
    """Members that of the vocabulary views

    Args:
        request (HttpRequest): Current request
        name (str): Name of the Vocabulary

    Raises:
        PermissionDenied: If current User lacks permission

    Returns:
        HttpResponse: A rendered Page
    """
    user = request.user
    vocabulary = Vocabulary.objects.get(name=voc_name)
    user_is_owner = 'owner' in get_perms(user, vocabulary)

    # put all users from groups and regulars into one list
    profiles_list = vocabulary.profiles.all()

    group_profile_list = vocabulary.groups.all()

    member_list = []

    for group in group_profile_list:
        g = {'name': group.group.name, 'description': group.description, 'type': group.__class__.__name__, 'role': 'Member'}
        member_list.append(g)

    for profile in profiles_list:
        g = {'name': profile.name, 'email': profile.user.email, 'type': profile.__class__.__name__, 'role': 'Owner' if profile.user.email == user.email else 'Member'}
        member_list.append(g)

    context = {
        'vocabulary': vocabulary,
        'members': member_list
    }

    if request.method == 'POST':
        if user_is_owner:
            if 'invite' in request.POST:
                invite_str = request.POST['email']

                # check if User/Group exists
                if User.objects.filter(email=invite_str).exists():
                    invite_user = User.objects.get(email=invite_str)
                    vocabulary.add_profile(invite_user.profile, 'participant')
                elif Group.objects.filter(name=invite_str).exists():
                    invite_group = Group.objects.get(name=invite_str)
                    vocabulary.add_group(
                        invite_group.groupprofile, 'participant')
                else:
                    return HttpResponse('User/Group does not exist', status=404)
            elif 'kickall' in request.POST:
                vocabulary.profiles.clear()
                vocabulary.groups.clear()
                vocabulary.add_profile(user.profile, 'owner')
            elif 'kick-member' in request.POST:
                type = request.POST['type']
                name_or_mail = request.POST['kick-member']
                if type == 'Profile':
                    user = User.objects.get(email=name_or_mail)
                    profile = vocabulary.profiles.get(user=user)
                    vocabulary.remove_profile(profile)
                else:
                    group = Group.objects.get(name=name_or_mail)
                    group_profile = vocabulary.groups.get(group=group)
                    vocabulary.remove_group(group_profile)
            # refresh page
            return redirect('vocabulary_members', vocabulary.name)

        else:
            raise PermissionDenied

    return render(request, 'vocabulary_members.html', context)


def terms(request: HttpRequest, voc_name: str) -> HttpResponse:
    """
    View for displaying all terms of a vocabulary
    Args:
        request (HttpRequest): request object
        name (str): vocabulary name

    Returns:
        HttpResponse: response object
    """

    vocabulary = Vocabulary.objects.get(name=voc_name)

    # get letter from querystring or default a
    letter = request.GET.get('letter') or 'a'
    # get page number from querystring or default 1
    page_number = int(request.GET.get('page') or 1)

    # pagination limit
    limit = 20
    # get all terms starting at offset
    offset = (page_number-1) * limit

    # A-Z select option
    form = Vocabulary_Terms_Form(
        initial={'initial_letter': (letter, letter.upper())})

    # get limit terms starting at offset starting with letter
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

    # query fuseki_dev and return json
    thing = fuseki_dev.query(vocabulary, query, 'json')

    # manipulate terms for easier templating
    terms = []
    for x in thing['results']['bindings']:
        sub = x['sub']['value']
        id = sub.split(vocabulary.urispace)[1]
        obj = x['obj']
        terms.append({'display_name': obj['value'], 'name': id})

    next_page_number = page_number + 1  # going over page limit does not matter
    previous_page_number = 1 if page_number - \
        1 == 0 else page_number-1  # dont go to page 0

    if request.method == 'POST':
        if 'create-term' in request.POST:
            term_name = request.POST['term-name']
            vocabulary.add_term(term_name)
            term = Term.objects.get(name=term_name)



    context = {
        'vocabulary': vocabulary,
        'terms': {'data': terms, 'next_page_number': next_page_number, 'previous_page_number': previous_page_number, 'start_index': offset, 'end_index': offset+len(terms)},
        'initial_letter': form,
    }
    return render(request, 'vocabulary_terms.html', context)

# TODO should get merged into the vocabulary dashboard view


def base(request: HttpRequest):
    user = request.user
    user_groups = user.groups.all()

    vocabulary_list = []
    for user_vocabulary in user.profile.vocabulary_set.all():
        vocabulary = {}
        vocabulary['vocabulary'] = user_vocabulary
        vocabulary_list.append(vocabulary)

    for review_voc in Vocabulary.objects.filter(state = 'Review'):
        vocabulary_list.append({'vocabulary' : review_voc})

    for group in user_groups:
        for group_vocabulary in group.groupprofile.vocabulary_set.all():
            vocabulary = {}
            vocabulary['team'] = group
            vocabulary['vocabulary'] = group_vocabulary 
            vocabulary_list.append(vocabulary)

    unique = []
    for v in vocabulary_list:
        x = False
        for v2 in unique:
            if v2['vocabulary'].name == v['vocabulary'].name:
                x = True
        if not x:
            unique.append(v)

    if request.method == 'POST':

        if 'create-vocabulary' in request.POST:
            try:
                voc_name = request.POST['name']
                urispace = request.POST['urispace']
                vocabulary = Vocabulary.create(
                    name=voc_name, urispace=urispace, creator=user.profile)
            except IntegrityError:
                return HttpResponse('vocabulary already exists')
            if 'file-upload' in request.FILES:
                import_voc = request.FILES['file-upload']
                vocabulary.import_vocabulary(input=import_voc)
            return redirect('base')


    search = request.GET.get('search')
    search_results = None
    if search != None:
        search_results = []
        # TODO: add filter for vocabulary
        for v in unique:
            vocabulary = v['vocabulary']
            # query all fields of the vocabulary
            query_result = fuseki_dev.query(vocabulary, """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

                SELECT DISTINCT ?s ?p ?o
                WHERE {{
                    ?s skos:prefLabel ?o .
                FILTER (strstarts(str(?o), '{0}'))
                }}
            """.format(search), 'json')

            for x in query_result['results']['bindings']:
                s = x['s']['value']
                value = x['o']['value']
                id = s.split(vocabulary.urispace)[1]
                search_results.append((id, value))

    context = {
        'user': request.user,
        'search_results': search_results,
        'search_term': search,
        'vocabulary_list' : unique,
        'user_groups' : user_groups,
    }

    return render(request, 'base.html', context)
