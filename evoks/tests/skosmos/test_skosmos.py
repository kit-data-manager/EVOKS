from django.test import TestCase
from django.conf import settings
from Skosmos.skosmos import Skosmos
from Skosmos.skosmos_vocabulary_config import SkosmosVocabularyConfig
from rdflib.namespace import URIRef
from rdflib import Graph


class SkosmosTest(TestCase):
    config_path = settings.SKOSMOS_TEST_CONFIG

    def setUp(self) -> None:
        self.skosmos = Skosmos(self.config_path)

        self.g = Graph()
        self.g.parse(self.skosmos.config_path, format='n3')

    def tearDown(self) -> None:
        config_file = open(self.skosmos.config_path, 'w', encoding='utf-8')
        config_file.write(self.g.serialize(format='turtle'))
        config_file.close()

    def test_add_vocabulary(self):
        try:
            config = SkosmosVocabularyConfig('cat_general', 'evoks', 'evoks', [
                'en'], 'http://localhost:3030/evoks/sparql', 'http://evoks.com/evoks', 'en')
            self.skosmos.add_vocabulary(config)

            g = Graph()
            g.parse(self.skosmos.config_path, format='n3', encoding='utf-8')
            #To print the graph g use: 
            #print(g.serialize(format="turtle"))

            added = False
            for s, p, o in g:
                if s == URIRef(self.skosmos._Skosmos__build_vocabulary_uri('evoks')):
                    added = True
            if not added:
                self.fail('No triples got added')
        except:
            self.fail('Adding vocabulary failed')

    def test_add_vocabulary_incorrect_config(self):
        config = SkosmosVocabularyConfig('cat_general', 'evoks', 'evoks', [
                'en'], 1111, 2222, 3333)
        self.assertRaises(TypeError, self.skosmos.add_vocabulary, config)

   
    def test_delete_vocabulary(self):
        try:
            self.skosmos.delete_vocabulary('unesco')
            g = Graph()
            g.parse(self.skosmos.config_path, format='n3')
            for s, p, o in g:
                if s == URIRef(self.skosmos._Skosmos__build_vocabulary_uri('unesco')):
                    self.fail('Triple still in config')
        except:
            self.fail('Deleting vocabulary failed')

    def test_delete_vocabulary_wrong_name(self):
        try:
            self.skosmos.delete_vocabulary('ontologe')
            g = Graph()
            g.parse(self.skosmos.config_path, format='n3')
            for s, p, o in g:
                if s == URIRef(self.skosmos._Skosmos__build_vocabulary_uri('ontologe')):
                    self.fail('Triple in config')
        except:
            self.fail('Something went wrongs')

  

                