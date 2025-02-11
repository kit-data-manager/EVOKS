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
    
    def export_term(self, dataformat: str) -> dict:
        """Exports a single term in the requested RDF format.

        Args:
            dataformat (str): Desired data format (json-ld, turtle, rdf+xml).

        Returns:
            dict: Dictionary containing file content, content type, and content disposition.
        """
        from evoks.fuseki import fuseki_dev
        from rdflib import Graph

        term_uri = f"{self.vocabulary.urispace}{self.uri}"

        # SPARQL query to get all triples related to the term
        query = f"""
            CONSTRUCT {{ <{term_uri}> ?p ?o }}
            WHERE {{ <{term_uri}> ?p ?o }}
        """

        try:
            rdf_graph = fuseki_dev.query(self.vocabulary, query, 'xml')

        except Exception as e:
            raise RuntimeError(f"Error fetching RDF data from Fuseki")

        # Format mapping for different RDF serialization options
        format_mapping = {
            "json-ld": ("json-ld", "application/ld+json", "jsonld"),
            "turtle": ("turtle", "text/turtle", "ttl"),
            "rdf+xml": ("xml", "application/rdf+xml", "rdf"),
        }

        if dataformat not in format_mapping:
            raise ValueError(f"Unsupported format: {dataformat}")

        rdf_format, content_type, file_extension = format_mapping[dataformat]

        file_content = rdf_graph.serialize(format=rdf_format, indent=2 if dataformat == "json-ld" else None)

        return {
            "file_content": file_content,
            "content_type": content_type,
            "content_disposition": f'attachment; filename={self.vocabulary.name}_{self.name}.{file_extension}',
        }


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
