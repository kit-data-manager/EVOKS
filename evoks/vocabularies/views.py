from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.template import loader
from SPARQLWrapper import SPARQLWrapper, JSON


def index(request):

#    sparql = SPARQLWrapper("http://fuseki-dev:3030/finnish-test")
#    sparql.setQuery("""
#        SELECT ?subject ?predicate ?object
#        WHERE {
#        ?subject ?predicate ?object
#        }
#        LIMIT 25
#    """)
#    sparql.setReturnFormat(JSON)
#    results = sparql.query().convert()
#    for result in results["results"]["bindings"]:
#        print(result)
#    print('---------------------------')

  
    if request.user.is_authenticated:
        vocabularies = Vocabulary.objects.all()
        template = loader.get_template('index.html')
        context = {
            'user': request.user,
            'vocabularies': vocabularies,
        }
        return HttpResponse(template.render(context, request))
    return HttpResponse('pls login')
