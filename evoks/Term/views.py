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
    # TODO turn slug into term name
    term = Term.objects.get(name=term_name)

    if request.method == 'POST':

        if 'delete-term' in request.POST:
            query = """
            DELETE {{ ?s ?p ?o . }} WHERE {{ VALUES ?s {{ <{0}> }} ?s ?p ?o }}
            """.format(vocabulary.urispace + term.name)
            fuseki_dev.query(vocabulary, query, 'json', 'update')
            term.delete()
            return redirect('vocabulary_overview', voc_name=vocabulary.name)

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
                {{ <{urispace}{term}> <{predicate}> {object} }}
                """.format(urispace=vocabulary.urispace, term=term.name, predicate=key, object=object)
                fuseki_dev.query(
                    vocabulary, query, 'xml', 'update')
            # edit field
            else:
                query += """
                DELETE {{ <{urispace}{term}> <{predicate}> {object} }}
                INSERT {{ <{urispace}{term}> <{predicate}> {new_object} }}
                WHERE
                {{ <{urispace}{term}> <{predicate}> {object} }}
                """.format(new_object=new_object, term=term.name, urispace=vocabulary.urispace, predicate=key, object=object)
                fuseki_dev.query(
                    vocabulary, query, 'xml', 'update')
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
            urispace = '<{0}{1}>'.format(vocabulary.urispace, term.name)
            vocabulary.create_field(urispace, predicate, object)
        
        elif 'download' in request.POST:
                dataformat = request.POST['download']
                result = term.export_term(dataformat)
                return result

    # put comments and tags on vocabulary into a list sorted from newest to oldest
    # TODO term
    comments = term.comment_set.filter()
    tags = term.tag_set.filter()
    activity_list = sorted(
        chain(comments, tags),
        key=lambda obj: str(obj.post_date), reverse=True)

    # add type of activity to activity list so we can render it differently
    for index, key in enumerate(activity_list):
        activity_list[index].type = key.__class__.__name__

    # query all fields of the vocabulary
    query_result = fuseki_dev.query(vocabulary, """
        SELECT * WHERE {{
            <{0}{1}> ?pred ?obj .
        }}
    """.format(vocabulary.urispace, term.name), 'json')

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

    print(activity_list)
    context = {
        'vocabulary': vocabulary,
        'fields': fields,
        'term': term,
        'activities': activity_list,

    }
    return render(request, 'term_detail.html', context)
