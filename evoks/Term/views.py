from django.http.request import HttpRequest
from django.shortcuts import render
from Term.models import Term
from vocabularies.models import Vocabulary

def term_detail(request : HttpRequest, name : str,term_name : str):
    vocabulary = Vocabulary.objects.get(name=name)
    #TODO turn slug into term name
    #term = Term.objects.get(name=term_name)
    context = {
        'vocabulary' : vocabulary
        #'term' : term
    }
    return render(request, 'term_detail.html', context)
