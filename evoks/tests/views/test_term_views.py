from django.test import TestCase
from django.test import Client
from unittest import skip

from django.contrib.auth.models import User, Group
from vocabularies.models import Vocabulary
from Term.models import Term
from evoks.fuseki import fuseki_dev
from evoks.skosmos import skosmos_dev, skosmos_live
from Term.views import convert_predicate, uri_validator
from Comment.models import Comment
from Tag.models import Tag


class Vocabulary_views_test(TestCase):
    @classmethod
    def setUp(self) -> None:
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        self.user.set_password('ok')
        self.user.profile.name = 'jhon'
        self.user.profile.verified = True
        self.user.save()
        self.vocabulary = Vocabulary.create(
            name='genel', urispace='http://www.testurispace.de', creator=self.user.profile)
        self.vocabulary.add_term('testsubject', 'testlabel')
        self.term = Term.objects.get(name='testsubject')
        self.c = Client()
        self.c.login(username='jhon@example.com', password='ok')
        self.group = Group.objects.create(name='hey')

    @classmethod
    def tearDown(self):
        # skosmos_dev.delete_vocabulary(self.vocabulary.name)
        try:
            fuseki_dev.delete_vocabulary(self.vocabulary)

        except:  # will fail when running the test_settings_delete testcase
            pass

    def test_convert_predicate(self):
        namespaces = self.vocabulary.get_namespaces()
        converted = convert_predicate(
            namespaces, 'http://www.w3.org/2004/02/skos/core#ConceptScheme')
        self.assertEqual(converted, 'skos:ConceptScheme')

    def test_uri_validator(self):
        self.assertTrue(uri_validator('http://github.com'))
        self.assertFalse(uri_validator('error'))

    # tests for term detail view

    def test_term_detail_template(self):
        response = self.c.get(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'delete-term': ''}
        )
        self.assertTemplateUsed(response, 'term_detail.html')

    def test_delete_term(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'delete-term': ''}
        )
        self.assertRedirects(
            response, '/vocabularies/{0}'.format(self.vocabulary.name))
        self.assertFalse(Term.objects.filter(name=self.term.name).exists())

    def test_comment(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'comment': '', 'comment-text': 'example comment'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'example comment')
        self.assertTrue(Comment.objects.filter(
            text='example comment').exists())

    def test_add_and_delete_tag(self):
        # create tag
        add_tag = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'tag': '', 'tag-name': 'example tag'},
            follow=True
        )
        self.assertEqual(add_tag.status_code, 200)
        self.assertContains(add_tag, 'example tag')
        self.assertTrue(Tag.objects.filter(name='example tag').exists())

        # delete tag
        delete_tag = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'delete-tag': 'example tag'},
            follow=True
        )
        self.assertEqual(delete_tag.status_code, 200)
        self.assertNotContains(delete_tag, 'example tag')
        self.assertFalse(Tag.objects.filter(name='example tag').exists())

    def test_download_ttl(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'download': 'turtle'},
        )
        self.assertEqual('{0}'.format(
            response), '<HttpResponse status_code=200, \"text/turtle\">')
        self.assertEqual(response.status_code, 200)

    def test_download_jsonld(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'download': 'json-ld'},
        )
        self.assertEqual('{0}'.format(
            response), '<HttpResponse status_code=200, \"application/ld+json\">')
        self.assertEqual(response.status_code, 200)

    def test_download_rdfxml(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'download': 'rdf+xml'},
        )
        self.assertEqual('{0}'.format(
            response), '<HttpResponse status_code=200, \"application/rdf+xml\">')
        self.assertEqual(response.status_code, 200)

    def test_create_property_empty_predicate(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'type': 'uri', 'object': 'abc'},
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_empty_type(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note', 'object': 'abc'},
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_empty_object(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note', 'type': 'uri'},
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_invalid_uri(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'uri', 'object': 'wa wa wa wa'},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_literal_invalid(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'literal', 'object': "'''"},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_invalid_lang(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'literal', 'object': 'testproperty', 'language': '////'},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_valid_lang(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'literal', 'object': 'testproperty', 'language': 'en'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'skos:note')
        self.assertContains(response, 'testproperty')
        self.assertContains(response, 'en')

    def test_create_uri_property(self):
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'uri', 'object': 'https://github.com/'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'skos:note')
        self.assertContains(response, 'https://github.com/')

    def test_edit_uri_field(self):
        # create field
        self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note',
                'obj-type': 'uri', 'object': 'https://github.com/'},
        )
        # edit field
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'obj': 'https://github.com/', 'key': 'skos:note', 'lang': '',
                'new-obj': 'https://gitlab.com/', 'obj-type': 'uri', 'obj-datatype': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'https://github.com/')
        self.assertContains(response, 'skos:note')

    def test_edit_literal_field(self):
        # create field
        self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note',
                'obj-type': 'literal', 'object': 'example label'},
        )

        # edit field
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'obj': 'example label', 'key': 'skos:note', 'lang': '',
                'new-obj': 'example field', 'obj-type': 'literal', 'obj-datatype': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'example label')
        self.assertContains(response, 'skos:note')

    def test_edit_uri_field_invalid_uri(self):
        # create field
        self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note',
                'obj-type': 'uri', 'object': 'https://github.com/'},
        )
        # edit field
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'obj': 'https://github.com/', 'key': 'skos:note', 'lang': '',
                'new-obj': 'error', 'obj-type': 'uri', 'obj-datatype': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_edit_literal_field_invalid_literal(self):
        # create field
        self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note',
                'obj-type': 'literal', 'object': 'example label'},
        )

        # edit field
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'obj': 'example label', 'key': 'skos:note', 'lang': '',
                'new-obj': "'''", 'obj-type': 'literal', 'obj-datatype': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_field(self):
        # create field
        self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'create-property': '', 'predicate': 'skos:note',
                'obj-type': 'literal', 'object': 'example label', 'lang': 'en'},
        )

        # delete field
        response = self.c.post(
            '/vocabularies/{0}/terms/{1}'.format(
                self.vocabulary.name, self.term.name),
            {'obj': 'example label', 'key': 'skos:note', 'lang': 'en',
                'new-obj': '', 'obj-type': 'literal', 'obj-datatype': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'example label')
