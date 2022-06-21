from django.http.request import HttpRequest
from django.shortcuts import render
from Term.models import Term
from vocabularies.models import Vocabulary
from itertools import chain
from evoks.fuseki import fuseki_dev
from typing import List, Tuple
from urllib.parse import urlparse
from Comment.models import Comment
from Tag.models import Tag
from django.shortcuts import redirect
from django.http import HttpResponse
from langcodes import Language
from vocabularies.forms import Property_Predicate_Form
from rdflib.namespace import _is_valid_uri
from vocabularies.views import get_vocab_perm

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


def term_detail(request: HttpRequest, voc_name: str, term_name: str):
    """View for the Term Detail Page

    Args:
        request (HttpRequest): request object
        name (str): name of vocabulary term is a part of
        term_slug (str): slug of the term name

    Returns:
        HttpResponse: Http Response object
    """
    user = request.user
    vocabulary = Vocabulary.objects.get(name=voc_name)
    term = Term.objects.get(name=term_name)
    # [HACK]
    # fix term name in header of term detail view
    # remove any trailing "_1" etc
    # TODO needs to be rethought, might cause problems in special term names
    # goes together with URI=Term etc (which might be set for usability)
    if term.name[-1:].isnumeric():
        name_stripped = term.name.split("_")[0]
    else:
        name_stripped = term.name
    # [/HACK]

    permission = get_vocab_perm(user, vocabulary)

    # broader option 2
    # TODO not suitable for large vocabs because too slow (could implement A-Z Dropdown or a search function)
    # get all terms of vocabulary for display list
    query_nofilter = """
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT DISTINCT ?sub ?pred ?obj
    WHERE {{
        ?sub skos:prefLabel ?obj .
    }}
    ORDER BY ?obj
    """


    thing_nofilter = fuseki_dev.query(vocabulary, query_nofilter, 'json')

    terms_nofilter = []
    for x in thing_nofilter['results']['bindings']:
        sub = x['sub']['value']
        id = sub.split(vocabulary.urispace)[1]
        terms_filtered = Term.objects.filter(uri=id, vocabulary=vocabulary)
        for singleterm in terms_filtered:
            obj = x['obj']
            # skip over current term such that a term cannot be chosen as broader term of itself
            if singleterm.name==term.name:
                continue
            terms_nofilter.append({'display_name': obj['value'], 'name': singleterm.name, 'fullid': vocabulary.urispace + singleterm.name})



    if request.method == 'POST':

        if 'delete-term' in request.POST and permission != 'spectator':
            query = """
            DELETE {{ ?s ?p ?o . }} WHERE {{ VALUES ?s {{ <{0}> }} ?s ?p ?o }}
            """.format(vocabulary.urispace + term.uri)
            fuseki_dev.query(vocabulary, query, 'json', 'update')
            term.delete()
            return redirect('vocabulary_overview', voc_name=vocabulary.name)

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

                    new_object = '<{0}>'.format(new_obj.rstrip())
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
                term.delete_field(key, object)
            # edit field
            else:
                term.edit_field(predicate=key, old_object=object, new_object=new_object)

        # create comment
        elif 'comment' in request.POST:
            comment_text = request.POST['comment-text']
            Comment.create(
                text=comment_text, author=user.profile, vocabulary=None, term=term)
            # refresh page so created comment is visible
            return redirect('term_detail', voc_name=vocabulary.name, term_name=term_name)

        # create tag
        elif 'tag' in request.POST:
            tag_name = request.POST['tag-name']

            # we only want 1 tag with the same name per vocabulary
            Tag.objects.filter(
                name=tag_name, term=term).delete()
            # create new tag
            Tag.create(
                name=tag_name, author=user.profile, vocabulary=None, term=term)
            return redirect('term_detail', voc_name = vocabulary.name, term_name=term_name)

        elif 'delete-tag' in request.POST:
            tag_name = request.POST['delete-tag']
            Tag.objects.filter(
                name=tag_name, term=term).delete()
            return redirect('term_detail', voc_name=voc_name, term_name=term_name)

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
                object_string = '{0}{1}'.format(vocabulary.urispace,object_string)
                # if uri is not valid its using a prefix and does not need braces
                if uri_validator(object_string) != True:
                    valid, object_string = vocabulary.convert_prefix(object_string)
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

            urispace = '<{0}{1}>'.format(vocabulary.urispace, term.uri)
            term.create_field(urispace, predicate, object)

        # # # TODO broader option 2
        # TODO check if type is really uri or literal
        # if type is literal, delete what is done with the uri and replace from above "if post is create property"
        elif 'create-broader' in request.POST and permission != 'spectator':
            if 'broader' not in request.POST:
                return HttpResponse('Empty broader', status=400)

            predicate_broader = "skos:broader"
            predicate_narrower = "skos:narrower"
            type = "uri"
            object_string =  request.POST['broader']

            # do if type is uri
            # if uri is not valid its using a prefix and does not need braces
            if uri_validator(object_string) != True:
                valid, object_string = vocabulary.convert_prefix(object_string)
                if not valid:
                    return HttpResponse('Invalid uri', status=400)

            if not _is_valid_uri(object_string):
                return HttpResponse('Invalid uri', status=400)
            
            object = '<{0}>'.format(object_string)

            urispace = '<{0}{1}>'.format(vocabulary.urispace, term.uri)
            # add skos:broader proerto to current term
            term.create_field(urispace, predicate_broader, object)
            
            # add skos:narrower property to broader term
            # TODO sollte überarbeitet werden, besser wäre wenn im create_broader nur der term.name übergeben wird
            # und die Uri hier in views zusammen gesetzt wird. Dann spart man sich das wenig robuste split("/")
            term_broader = Term.objects.get(name=object_string.split("/")[-1])
            term_broader.create_field(object, predicate_narrower, urispace)
        
        elif 'download' in request.POST:
                dataformat = request.POST['download']
                export = term.export_term(dataformat)
                response = HttpResponse(
                    export['file_content'], export['content_type'])
                response['Content-Disposition'] = export['content_disposition']
                return response

    # put comments and tags on term into a list sorted from newest to oldest
    comments = term.comment_set.filter()
    tags = term.tag_set.filter()
    activity_list = sorted(
        chain(comments, tags),
        key=lambda obj: str(obj.post_date), reverse=True)

    # add type of activity to activity list so we can render it differently
    for index, key in enumerate(activity_list):
        activity_list[index].type = key.__class__.__name__

    # query all fields of the term
    query_result = fuseki_dev.query(vocabulary, """
        SELECT * WHERE {{
            <{0}{1}> ?pred ?obj .
        }}
    """.format(vocabulary.urispace, term.uri), 'json')

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
            obj['lang_display'] = Language.get(obj['xml:lang']).display_name() 

        # append object to list of objects with same predicate
        fields[pred]['objects'].append(obj)
    form = Property_Predicate_Form(initial={'predicate': 'skos:altLabel', 'prefix': 'skos'})

    context = {
        'vocabulary': vocabulary,
        'fields': fields,
        'term': term,
        'name_stripped': name_stripped,
        'activities': activity_list,
        'terms_nofilter': {'data': terms_nofilter, },
        'form' : form,
    }
    return render(request, 'term_detail.html', context)
