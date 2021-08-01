from django.test import TestCase
from Skosmos.skosmos_vocabulary_config import SkosmosVocabularyConfig


class SkosmosVocabularyConfigTest(TestCase):

    def test_config_equal_to_input(self):
        subject = "Alkoholkonsum der Studenten"
        title = "Bier"
        name = "beer"
        languages = "Vodka, Rum"
        sparql_endpoint = "http:Schnaps"
        uri_space = "http:schnaps"
        default_language = "Vodka"

        config = SkosmosVocabularyConfig(
            subject, title, name, languages, sparql_endpoint, uri_space, default_language)

        self.assertEqual(config.subject, subject)
        self.assertEqual(config.title, title)
        self.assertEqual(config.languages, languages)
        self.assertEqual(config.sparql_endpoint, sparql_endpoint)
        self.assertEqual(config.uri_space, uri_space)
        self.assertEqual(config.default_language, default_language)
