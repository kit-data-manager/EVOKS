from django.db import models
from django.db.models.deletion import CASCADE
import json
from django.http import HttpResponse
import requests
from django.conf import settings

# Create your models here.


class Term(models.Model):
    name = models.SlugField(max_length=50, unique=True)
    vocabulary = models.ForeignKey(
        to='vocabularies.Vocabulary', on_delete=CASCADE, blank=True, null=True)

    @classmethod
    def create(cls, name: str):
        """Creates a Term

        Args:
            name (str): Name of the Term
        """
        term = cls(name=name)
        term.save()
        return term

    def export_term(self, data_format: str) -> None:
        from evoks.fuseki import fuseki_dev

        query = """
            SELECT ?subject ?predicate ?object
            WHERE {{
            <{0}{1}> ?predicate ?object
            }}""".format(self.vocabulary.urispace, self.name)
        if data_format == 'json':
            thing = fuseki_dev.query(self.vocabulary, query, 'json')
            file_content = json.dumps(thing, indent=4, sort_keys=True)
            response = HttpResponse(
                file_content, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename={0}.json'.format(
                self.name)
            return response
        elif data_format == 'N3':
            thing = fuseki_dev.query(self.vocabulary, """
            DESCRIBE <{0}{1}> """.format(self.vocabulary.urispace, self.name), 'N3')
            file_content = thing.serialize(format='n3')
            response = HttpResponse(
                file_content, content_type='application/ttl')
            response['Content-Disposition'] = 'attachment; filename={0}.ttl'.format(
                self.name)
            return response
        elif data_format == 'rdf/xml':
            thing = fuseki_dev.query(self.vocabulary, query, 'xml')
            file_content = thing.toprettyxml()
            response = HttpResponse(
                file_content, content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename={0}.xml'.format(
                self.name)
            return response
