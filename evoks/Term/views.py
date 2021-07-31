from django.http.request import HttpRequest
from django.shortcuts import render
from Term.models import Term
from vocabularies.models import Vocabulary
from itertools import chain

def term_detail(request : HttpRequest, name : str,term_slug : str):
    """View for the Term Detail Page

    Args:
        request (HttpRequest): request object
        name (str): name of vocabulary term is a part of
        term_slug (str): slug of the term name

    Returns:
        HttpResponse: Http Response object
    """

    vocabulary = Vocabulary.objects.get(name=name)
    #TODO turn slug into term name
    #term = Term.objects.get(name=term_name)

    # put comments and tags on vocabulary into a list sorted from newest to oldest
    #TODO term
    comments = vocabulary.comment_set.filter()
    tags = vocabulary.tag_set.filter()
    activity_list = sorted(
        chain(comments, tags),
        key=lambda obj: str(obj.post_date), reverse=True)

    # add type of activity to activity list so we can render it differently
    for index, key in enumerate(activity_list):
        activity_list[index].type = key.__class__.__name__



    context = {
        'vocabulary' : vocabulary
        #'term' : term
    }
    return render(request, 'term_detail.html', context)
