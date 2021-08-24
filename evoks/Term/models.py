from django.db import models
from django.db.models.deletion import CASCADE
import json
from django.http import HttpResponse
import requests
from django.conf import settings

# Create your models here.


class Term(models.Model):
    name = models.SlugField(max_length=50, unique=True)
    uri = models.CharField(max_length=200, unique=False, default='')
    vocabulary = models.ForeignKey(
        to='vocabularies.Vocabulary', on_delete=CASCADE, blank=True, null=True)

    @classmethod
    def create(cls, name: str, uri: str):
        """Creates a Term

        Args:
            name (str): Name of the Term
        """
        term = cls(name=name, uri=uri)
        term.save()
        return term

    def export_term(self, data_format: str) -> None:
        from evoks.fuseki import fuseki_dev

        query = """
            SELECT ?subject ?predicate ?object
            WHERE {{
            <{0}{1}> ?predicate ?object
            }}""".format(self.vocabulary.urispace, self.uri)
        if data_format == 'json-ld':
            thing = fuseki_dev.query(self.vocabulary, """
            DESCRIBE <{0}{1}> """.format(self.vocabulary.urispace, self.uri), 'xml')
            file_content = thing.serialize(format='json-ld')
            content_type = 'application/json-ld'
            content_disposition = 'attachment; filename={0}_{1}.jsonld'.format(
                self.vocabulary.name, self.name)
        elif data_format == 'turtle':
            thing = fuseki_dev.query(self.vocabulary, """
            DESCRIBE <{0}{1}> """.format(self.vocabulary.urispace, self.uri), 'xml')
            file_content = thing.serialize(format='n3')
            content_type = 'application/ttl'
            content_disposition = 'attachment; filename={0}_{1}.ttl'.format(
                self.vocabulary.name, self.name)
        elif data_format == 'rdf+xml':
            thing = fuseki_dev.query(self.vocabulary, query, 'xml')
            file_content = thing.toprettyxml()
            content_type = 'application/rdf+xml'
            content_disposition = 'attachment; filename={0}_{1}.rdf'.format(
                self.vocabulary.name, self.name)

        export = {
            'file_content': file_content,
            'content_type': content_type,
            'content_disposition': content_disposition
        }
        return export

    def edit_field(self, predicate: str, old_object: str, new_object: str) -> None:
        """Replaces the object of a triple field with a new object, by using SPARQL Queries and the Fuseki-Dev Instance

        Args:
            predicate (str): Predicate of the triple
            old_object (str): Old object of the triple
            new_object (str): New object of the triple
        """
        from evoks.fuseki import fuseki_dev

        namespaces = self.vocabulary.get_namespaces()
        query = self.vocabulary.prefixes_to_str(namespaces)
        query += """
            DELETE {{ <{urispace}{term}> <{predicate}> {old_object} }}
            INSERT {{ <{urispace}{term}> <{predicate}> {new_object} }}
            WHERE
            {{ <{urispace}{term}> <{predicate}> {old_object} }}
        """.format(urispace=self.vocabulary.urispace, term=self.uri,
                   predicate=predicate, old_object=old_object, new_object=new_object)
        fuseki_dev.query(
            self.vocabulary, query, 'xml', 'update')

    def create_field(self, urispace: str, predicate: str, object: str) -> None:
        """Creates a Triple Field on the Fuseki-Dev Instance

        Args:
            urispace (str): urispace of the vocabulary and subject of the triple
            predicate (str): predicate of the triple
            object (str): object of the triple
        """
        from evoks.fuseki import fuseki_dev

        namespaces = self.vocabulary.get_namespaces()
        query = self.vocabulary.prefixes_to_str(namespaces)

        query += 'INSERT DATA {{ {0} {1} {2} }}'.format(
            urispace, predicate, object)
        fuseki_dev.query(vocabulary=self.vocabulary, query=str(
            query), return_format='json', endpoint='update')

    def delete_field(self, predicate: str, object: str) -> None:
        """Deletes a Triple Field of the term on the Fuseki-Dev Instance

        Args:
            predicate (str): Predicate of the triple
            object (str): Object of the triple
        """
        from evoks.fuseki import fuseki_dev

        namespaces = self.vocabulary.get_namespaces()
        query = self.vocabulary.prefixes_to_str(namespaces)
        query += """
            DELETE DATA
            {{ <{urispace}{term}> <{predicate}> {object} }}
            """.format(urispace=self.vocabulary.urispace, term=self.uri, predicate=predicate, object=object)
        fuseki_dev.query(
            self.vocabulary, query, 'xml', 'update')
