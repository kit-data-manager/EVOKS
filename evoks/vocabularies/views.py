from enum import unique
from django.http.request import HttpRequest
from django.http.response import HttpResponseBadRequest
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
from langcodes import Language
from evoks.settings import SKOSMOS_LIVE_URI, SKOSMOS_DEV_URI
from django.core.exceptions import PermissionDenied
from .forms import Property_Predicate_Form, Vocabulary_Terms_Form, CreateVocabularyForm
from Tag.models import Tag
from evoks.fuseki import fuseki_dev
from Comment.models import Comment
from itertools import chain
from guardian.shortcuts import get_perms
from django.contrib.auth.decorators import login_required, user_passes_test
from rdflib.namespace import _is_valid_uri
import re
from unidecode import unidecode

def prefixes(request: HttpRequest, voc_name: str) -> HttpResponse:
    """Views for prefixes tab

    Args:
        request (HttpRequest): request object
        name (HttpResponse): name of vocabulary

    Returns:
        HttpResponse: HttpResponse
    """
    vocabulary = Vocabulary.objects.get(name=voc_name)
    user = request.user
    permission = get_vocab_perm(user, vocabulary)

    if permission != 'spectator':
        if request.method == 'POST':
            prefixes = request.POST['prefixes'].split(
                '\r\n')  # could lead to problems with \r\n
            # remove all empty lines
            non_empty_prefixes = [
                line for line in prefixes if line.strip() != ""]
            if vocabulary.validate_prefixes(non_empty_prefixes):
                vocabulary.prefixes = non_empty_prefixes  # save prefixes in vocabulary
                vocabulary.save()
            else:
                return HttpResponse('The given Prefix does not fit the required format', status=400)

        template = loader.get_template('vocabulary_prefixes.html')
        context = {
            'user': request.user,
            'vocabulary': vocabulary,
            'prefixes': '\n'.join(vocabulary.prefixes),
        }

        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse('Insufficient permissions', status=403)


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


def get_vocab_perm(user: User, vocabulary: Vocabulary) -> str:
    """Gets the highest permission that the User has on the Vocabulary

    Args:
        user (User): User

    Returns:
        str: Highest permission
    """
    permission = 'spectator'
    # check for permissions given by groups that the user is part of
    for group in user.groups.all():
        if 'owner' in get_perms(group, vocabulary):
            permission = 'owner'
            return permission
        elif 'participant' in get_perms(group, vocabulary):
            permission = 'member'
    # checks for permissions of user
    if 'owner' in get_perms(user, vocabulary):
        permission = 'owner'
    elif 'participant' in get_perms(user, vocabulary):
        permission = 'member'
    return permission


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
    permission = get_vocab_perm(user, vocabulary)

    form = Property_Predicate_Form(initial={'predicate': 'skos:Concept'})

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

        if 'obj' in request.POST and permission != 'spectator':
            key = request.POST['key']
            obj = request.POST['obj']
            lang = request.POST['lang']
            datatype = request.POST['obj-datatype']
            new_obj = request.POST['new-obj']
            type = request.POST['obj-type']

            # if we want to edit a field
            if new_obj != '':
                if type == 'uri':
                    # if uri is not valid its using a prefix and does not need braces
                    if uri_validator(new_obj) != True:
                        valid, new_obj = vocabulary.convert_prefix(new_obj)
                        if not valid:
                            return HttpResponse('Invalid uri', status=400)

                    if not _is_valid_uri(new_obj):
                        return HttpResponse('Invalid uri', status=400)

                    new_object = '<{0}>'.format(new_obj)
                else:
                    if "'''" in new_obj:
                        return HttpResponse('Literal cannot contain \'\'\'', status=400)
                    new_object = '\'\'\'{0}\'\'\''.format(new_obj)
                    if lang != '':  # add lang tag if it exists
                        new_object += '@{0}'.format(lang)
                    elif datatype != '':  # add datatype if it exists
                        new_object += '^^<{0}>'.format(datatype)

            # format the old object correctly
            if type == 'uri':
                if uri_validator(obj) != True:
                    object = obj
                else:
                    object = '<{0}>'.format(obj)
            else:
                object = '\'\'\'{0}\'\'\''.format(obj)
                if lang != '':
                    object += '@{0}'.format(lang)
                elif datatype != '':  # add datatype if it exists
                    object += '^^<{0}>'.format(datatype)

            # delete field
            if new_obj == '':
                vocabulary.delete_field(key, object)

            # edit field
            else:
                vocabulary.edit_field(
                    predicate=key, old_object=object, new_object=new_object)

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

        elif 'create-property' in request.POST and permission != 'spectator':
            if 'predicate' not in request.POST:
                return HttpResponse('Empty predicate', status=400)
            if 'type' not in request.POST:
                return HttpResponse('Empty type', status=400)
            if 'object' not in request.POST or request.POST['object'] == '':
                return HttpResponse('Empty object', status=400)

            predicate = request.POST['predicate']

            type = request.POST['type']
            object_string = request.POST['object']
            if type == 'uri':
                # if uri is not valid its using a prefix and does not need braces
                if uri_validator(object_string) != True:
                    namespaces = vocabulary.get_namespaces()
                    valid, object_string = vocabulary.convert_prefix(
                        object_string)
                    if not valid:
                        return HttpResponse('Invalid uri', status=400)

                if not _is_valid_uri(object_string):
                    return HttpResponse('Invalid uri', status=400)

                object = '<{0}>'.format(object_string)
            else:
                if "'''" in object_string:
                    return HttpResponse('Literal cannot contain \'\'\'', status=400)
                object = '\'\'\'{0}\'\'\''.format(object_string)
                if 'language' in request.POST and request.POST['language'] != '':
                    try:
                        language = Language.get(request.POST['language'])
                        if not language.is_valid() or type == 'uri':
                            return HttpResponse('Invalid language', status=400)
                        object += '@{0}'.format(language.language)
                    except:
                        return HttpResponse('Invalid language', status=400)
                elif 'datatype' in request.POST and request.POST['datatype'] != '':
                    object += '^^<{0}>'.format(request.POST['datatype'])

            urispace = '<{0}>'.format(vocabulary.urispace)
            vocabulary.create_field(urispace, predicate, object)

        elif 'download' in request.POST:
            dataformat = request.POST['download']
            export = vocabulary.export_vocabulary(dataformat)
            response = HttpResponse(
                export['file_content'], export['content_type'])
            response['Content-Disposition'] = export['content_disposition']
            return response

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
            obj['lang_display'] = Language.get(
                obj['xml:lang']).display_name()

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
            FILTER (strstarts(lcase(str(?o)), '{0}'))
            }}
            LIMIT 50
        """.format(search.lower()), 'json')

        for x in query_result['results']['bindings']:
            s = x['s']['value']
            value = x['o']['value']

            split = s.split(vocabulary.urispace)
            if len(split) > 1:
                id = s.split(vocabulary.urispace)[1]
                terms = Term.objects.filter(uri=id, vocabulary=vocabulary)
                for term in terms:
                    path = vocabulary.name + '/terms/' + term.name
                    search_results.append(
                        (path, '{0}: {1}'.format(vocabulary.name, value)))

    template = loader.get_template('vocabulary.html')
    skosmos_url = SKOSMOS_DEV_URI if vocabulary.state == State.REVIEW else SKOSMOS_LIVE_URI
    context = {
        'user': request.user,
        'vocabulary': vocabulary,
        'fields': fields,
        'activities': activity_list,
        'search_results': search_results,
        'search_term': search,
        'skosmos_url': '{0}{1}-{2}'.format(skosmos_url, vocabulary.name, str(vocabulary.version-1 if vocabulary.state == 'Live' else vocabulary.version)),
        'form': form,
    }
    return HttpResponse(template.render(context, request))


def settings(request: HttpRequest, voc_name: str):
    """View for settings tab on a vocabulary

    Args:
        request (HttpRequest): Current request
        name (str): Name of the vocabulary

    Returns:
        HttpResponse: Rendered Settings Site
    """
    vocabulary = Vocabulary.objects.get(name=voc_name)
    user = request.user
    permission = get_vocab_perm(user, vocabulary)
    context = {
        'user': user,
        'vocabulary': vocabulary
    }

    if request.method == 'POST':
        if permission == 'owner':
            # delete vocabulary
            if 'delete' in request.POST:
                if vocabulary.state == State.REVIEW:
                    skosmos_dev.delete_vocabulary(
                        vocabulary.name_with_version())
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
    permission = get_vocab_perm(user, vocabulary)

    owners = 0
    for profile in vocabulary.profiles.all():
        if 'owner' in get_perms(profile.user, vocabulary):
            owners += 1
    for group in vocabulary.groups.all():
        if 'owner' in get_perms(group.group, vocabulary):
            owners += 1


    # put all users from groups and regulars into one list
    profiles_list = vocabulary.profiles.all()

    group_profile_list = vocabulary.groups.all()

    member_list = []

    for group in group_profile_list:
        g = {'name': group.group.name, 'description': group.description,
             'type': group.__class__.__name__, 'member': group.group}
        member_list.append(g)

    for profile in profiles_list:
        g = {'name': profile.name, 'email': profile.user.email,
             'type': profile.__class__.__name__, 'member': profile.user}
        member_list.append(g)

    context = {
        'user': user,
        'vocabulary': vocabulary,
        'members': member_list
    }

    if request.method == 'POST':
        if permission == 'owner':
            if 'invite' in request.POST:
                invite_str = request.POST['email']

                # check if User/Group exists
                if User.objects.filter(email=invite_str).exists():
                    invite_user = User.objects.get(email=invite_str)
                    if invite_user.profile in vocabulary.profiles.all():
                        return HttpResponse('already in Vocabulary', status=400)
                    else:
                        vocabulary.add_profile(
                            invite_user.profile, 'participant')
                elif Group.objects.filter(name=invite_str).exists():
                    invite_group = Group.objects.get(name=invite_str)
                    if invite_group.groupprofile in vocabulary.groups.all():
                        return HttpResponse('already in Vocabulary', status=400)
                    else:
                        vocabulary.add_group(
                            invite_group.groupprofile, 'participant')
                else:
                    return HttpResponse('User/Group does not exist', status=404)
            elif 'kickall' in request.POST:
                for profile in vocabulary.profiles.all():
                    vocabulary.remove_profile(profile)
                for group in vocabulary.groups.all():
                    vocabulary.remove_group(group)
                vocabulary.add_profile(user.profile, 'owner')
            elif 'role' in request.POST:
                role = request.POST['role']
                name_or_mail = request.POST['nameormail']
                type = request.POST['type']
                if type == 'Profile':
                    changed_user = User.objects.get(email=name_or_mail)
                    # cant change perm if only owner
                    if owners <= 1 and 'owner' in get_perms(changed_user, vocabulary):
                        return HttpResponse('Cannot change role of last owner', status=400)
                    vocabulary.change_profile_perm(changed_user.profile, role)
                else:
                    group = Group.objects.get(name=name_or_mail)
                    # cant change perm if only owner
                    if owners <= 1 and 'owner' in get_perms(group, vocabulary):
                        return HttpResponse('Cannot change role of last owner', status=400)
                    vocabulary.change_group_perm(group.groupprofile, role)

            elif 'kick-member' in request.POST:
                type = request.POST['type']
                name_or_mail = request.POST['kick-member']
                if type == 'Profile':
                    kicked_user = User.objects.get(email=name_or_mail)
                    # cant kick only owner
                    if owners <= 1 and 'owner' in get_perms(kicked_user, vocabulary):
                        return HttpResponse('Cannot kick last owner', status=400)
                    vocabulary.remove_profile(kicked_user.profile)
                else:
                    group = Group.objects.get(name=name_or_mail)
                    # cant kick only owner
                    if owners <= 1 and 'owner' in get_perms(group, vocabulary):
                        return HttpResponse('Cannot kick last owner', status=400)
                    vocabulary.remove_group(group.groupprofile)
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
    user = request.user
    vocabulary = Vocabulary.objects.get(name=voc_name)
    permission = get_vocab_perm(user, vocabulary)

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
        terms_filtered = Term.objects.filter(uri=id, vocabulary=vocabulary)
        for term in terms_filtered:
            obj = x['obj']
            terms.append({'display_name': obj['value'], 'name': term.name})

    next_page_number = page_number + 1  # going over page limit does not matter
    previous_page_number = 1 if page_number - \
        1 == 0 else page_number-1  # dont go to page 0

    if request.method == 'POST':
        if 'create-term' in request.POST and permission != 'spectator':
            # term_subject = request.POST['term-subject']
            term_label = request.POST['term-label']
            # remove german umlaute
            term_subject = term_label.replace(" ", "")
            term_subject = term_subject.replace("ü","ue")
            term_subject = term_subject.replace("ö","oe")
            term_subject = term_subject.replace("ä","ae")
            term_subject = term_subject.replace("ß","ss")
            # transfer non standard chars like greek into alphanumeric chars
            term_subject = unidecode(term_subject)
            # remove any special chars
            term_subject = re.sub(r'[^a-zA-Z0-9]', '', term_subject)

            if not (bool(re.match('^[a-zA-Z0-9]+$', term_subject))):
                return HttpResponseBadRequest('invalid subject')

            term_name = term_subject.replace('/', '_')

            # check if term already exists
            # HACK TODO
            # this is wrongly implemented
            # when the term exists in another vocabulary, it cannot be created
            # should only fail if the term already exists in the current vocabulary
            # current HACK is just to remove the check if term exists already
            # if Term.objects.filter(uri=term_subject).exists():
                # return HttpResponse('term exists already', status=409)

            # find unique evoks url for term
            name = term_name
            i = 1
            while Term.objects.filter(name=name).exists():
                name = '{0}_{1}'.format(term_name, i)
                i += 1

            if not _is_valid_uri(vocabulary.urispace + term_subject):
                return HttpResponseBadRequest('invalid subject')

            if "'''" in term_label:
                return HttpResponseBadRequest('prefLabel cannot contain \'\'\'', status=400)

            vocabulary.add_term(name, term_subject)

            # insert into vocabulary
            object = '\'\'\'{0}\'\'\''.format(term_label)
            urispace = '<{0}{1}>'.format(
                vocabulary.urispace, term_subject.rstrip())
            predicate = '<http://www.w3.org/2004/02/skos/core#prefLabel>'
            vocabulary.create_field(urispace, predicate, object)
            vocabulary.create_field(urispace, '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>',
                                    '<http://www.w3.org/2004/02/skos/core#Concept>')
            # redirect to new term
            return redirect('term_detail', voc_name=vocabulary.name, term_name=name)

    context = {
        'user': user,
        'vocabulary': vocabulary,
        'terms': {'data': terms, 'next_page_number': next_page_number, 'previous_page_number': previous_page_number, 'start_index': offset, 'end_index': offset+len(terms)},
        'initial_letter': form,
    }
    return render(request, 'vocabulary_terms.html', context)


def base(request: HttpRequest):
    user = request.user
    user_groups = user.groups.all()

    vocabulary_list = []
    for user_vocabulary in user.profile.vocabulary_set.all():
        vocabulary = {}
        vocabulary['vocabulary'] = user_vocabulary
        vocabulary_list.append(vocabulary)

    for review_voc in Vocabulary.objects.filter(state='Review'):
        vocabulary_list.append({'vocabulary': review_voc})

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
            form = CreateVocabularyForm(request.POST)
            if form.is_valid():
                voc_name = form.cleaned_data['name']
                

                # HACK hier wird der URIspace einfach aus dem Name generiert (aber nur wenn nichts importiert wird). 
                # sorgt dafür, dass der Name eines erstellten Vokabulars unique sein muss, das muss verbessert werden
                # TODO
                # unhacked ->
                # urispace = form.cleaned_data['urispace']
                # <-
                # urispace = 'http://{0}.org/'.format(voc_name)
                urispace = ''


            else:
                return HttpResponse('Invalid form', status=400)
            try:
                if 'file-upload' not in request.FILES:
                    urispace = 'http://{0}.org/'.format(voc_name)
                if urispace == '' and 'file-upload' not in request.FILES:
                    return HttpResponseBadRequest('empty urispace is not allowed when creating a new vocabulary')

                if urispace != '' and (not uri_validator(urispace) or not _is_valid_uri(urispace)):
                    return HttpResponseBadRequest('invalid urispace')

                vocabulary = Vocabulary.create(
                    name=voc_name, urispace=urispace, creator=user.profile)
                vocabulary.create_field('<{}>'.format(
                    urispace), '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>', '<http://www.w3.org/2004/02/skos/core#ConceptScheme>')

            except IntegrityError:
                return HttpResponse('vocabulary already exists', status=409)
            if 'file-upload' in request.FILES:
                try:
                    import_voc = request.FILES['file-upload']
                    vocabulary.import_vocabulary(input=import_voc)
                except ValueError as e:
                    try:
                        fuseki_dev.delete_vocabulary(vocabulary)
                        vocabulary.delete()
                    except Exception as e:
                        pass
                    return HttpResponse('Importing vocabulary failed', status=400)

            return redirect('base')

    search = request.GET.get('search')
    search_results = None
    if search != None:
        search_results = []
        for v in unique:
            vocabulary = v['vocabulary']
            # query all fields of the vocabulary
            query_result = fuseki_dev.query(vocabulary, """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

                SELECT DISTINCT ?s ?p ?o
                WHERE {{
                    ?s skos:prefLabel ?o .
                FILTER (strstarts(lcase(str(?o)), '{0}'))
                }}
            """.format(search.lower()), 'json')

            for x in query_result['results']['bindings']:
                s = x['s']['value']
                value = x['o']['value']
                split = s.split(vocabulary.urispace)
                if len(split) > 1:
                    id = s.split(vocabulary.urispace)[1]
                    terms = Term.objects.filter(uri=id, vocabulary=vocabulary)
                    for term in terms:
                        path = '{0}/terms/{1}'.format(
                            vocabulary.name, term.name)
                        search_results.append(
                            (path, '{0}: {1}'.format(vocabulary.name, value)))

    context = {
        'user': request.user,
        'search_results': search_results,
        'search_term': search,
        'vocabulary_list': unique,
        'user_groups': user_groups,
    }

    return render(request, 'base.html', context)
