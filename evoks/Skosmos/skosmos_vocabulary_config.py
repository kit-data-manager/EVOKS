from typing import List


class SkosmosVocabularyConfig:
    """This class stores all skosmos config parameters
    """

    def __init__(self, subject: str, title: str, name: str, languages: List[str], sparql_endpoint: str, uri_space: str, default_language: str):
        """Constructor of SkosmosVocabularyConfig

        Args:
            subject (str): Subject of the vocabulary
            title (str): Title of the vocabulary
            languages (List[str]): List of available languages
            sparql_endpoint (str): SPARQL endpoint of vocabulary
            uri_space (str): URI space of vocabulary
            default_language (str): Default language of vocabulary
        """
        self.subject = subject
        self.title = title
        self.languages = languages
        self.sparql_endpoint = sparql_endpoint
        self.uri_space = uri_space
        self.default_language = default_language
        self.name = name