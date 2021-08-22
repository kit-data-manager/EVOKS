from rdflib import Graph, Literal
from rdflib.namespace import URIRef, Namespace, SKOS, VOID
from django.conf import settings
import os
from pathlib import Path
from .skosmos_vocabulary_config import SkosmosVocabularyConfig


class Skosmos:

    def __init__(self, config_path: str) -> None:
        self.config_path = self.__build_config_path(config_path)

        valid = os.path.exists(self.config_path)
        if not valid:
            raise ValueError('Skosmos config path is not valid')

    def __build_config_path(self, config_path: str) -> str:
        return os.path.join(settings.DOCKER_BASE_DIR, config_path)

    def __build_vocabulary_uri(self, vocabulary_name: str) -> str:
        return '{path}#{name}'.format(path=Path(self.config_path).as_uri(), name=vocabulary_name)

    def __print_graph(self) -> None: # pragma: no cover
        g = Graph()
        g.parse(self.config_path, format="n3")
        for stmt in g:
            print(stmt)

    def delete_vocabulary(self, vocabulary_name: str) -> None:
        """[summary]
        Deletes the given vocabulary from the Skosmos config

        Args:
            vocabulary_name (str): unique name of vocabulary that gets deleted
        """
        g = Graph()

        vocabulary_uri = URIRef(
            self.__build_vocabulary_uri(vocabulary_name))
        g.parse(self.config_path, format='n3')
        g.remove((vocabulary_uri, None, None))

        config_file = open(self.config_path, 'w')
        config_file.write(g.serialize(format='turtle'))
        config_file.close()

    def add_vocabulary(self, config: SkosmosVocabularyConfig) -> None:

        g = Graph()

        DC = Namespace('http://purl.org/dc/terms/')
        g.bind('void', VOID)
        g.bind('dc', DC)
        g.bind('skos', SKOS)

        g.parse(self.config_path, format="n3")

        vocabulary_uri = self.__build_vocabulary_uri(config.name)

        g.add((URIRef(vocabulary_uri),
              URIRef('http://purl.org/net/skosmos#fullAlphabeticalIndex'), Literal(True)))

        g.add((URIRef(vocabulary_uri),
              URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), URIRef('http://purl.org/net/skosmos#Vocabulary')))

        g.add((URIRef(vocabulary_uri),
              URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'), URIRef('http://rdfs.org/ns/void#Dataset')))

        g.add((URIRef(vocabulary_uri), DC.title, Literal(config.title)))

        g.add((URIRef(vocabulary_uri),
              URIRef('http://purl.org/net/skosmos#defaultLanguage'), Literal(config.default_language)))

        for language in config.languages:
            g.add((URIRef(vocabulary_uri),
              URIRef('http://purl.org/net/skosmos#language'), Literal(language)))


        g.add((URIRef(vocabulary_uri),
              URIRef('http://purl.org/net/skosmos#mainConceptScheme'), URIRef(config.uri_space)))

        g.add((URIRef(vocabulary_uri),
              DC.subject, URIRef(self.__build_vocabulary_uri(config.subject))))

        g.add((URIRef(vocabulary_uri),
              URIRef('http://rdfs.org/ns/void#sparqlEndpoint'), URIRef(config.sparql_endpoint)))

        g.add((URIRef(vocabulary_uri),
              URIRef('http://rdfs.org/ns/void#uriSpace'), Literal(config.uri_space)))

        f = open(self.config_path, "w")
        f.write(g.serialize(format="turtle"))
