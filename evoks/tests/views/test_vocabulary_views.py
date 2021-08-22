from django.test import TestCase
from django.test import Client
from unittest import skip

from django.contrib.auth.models import User, Group
from vocabularies.models import Vocabulary
from Term.models import Term
from Comment.models import Comment
from Tag.models import Tag
from evoks.fuseki import fuseki_dev, fuseki_live
from evoks.skosmos import skosmos_dev, skosmos_live
from guardian.shortcuts import get_perms


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
        self.c = Client()
        self.c.login(username='jhon@example.com', password='ok')
        self.group = Group.objects.create(name='hey')

    @classmethod
    def tearDown(self):
        try:
            skosmos_dev.delete_vocabulary(self.vocabulary.name_with_version())
            skosmos_live.delete_vocabulary(self.vocabulary.name_with_version())
            fuseki_dev.delete_vocabulary(self.vocabulary)
            fuseki_live.delete_vocabulary(self.vocabulary, True)
        except:  # will fail when running the test_settings_delete testcase
            pass

    # prefix view tests

    def test_prefix_view(self):
        get = self.c.get(
            '/vocabularies/{0}/prefixes'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, 'vocabulary_prefixes.html')
        response = self.c.post(
            '/vocabularies/{0}/prefixes'.format(self.vocabulary.name),
            {'prefixes': 'PREFIX xls: <http://xmlns.com/foaf/0.1/>'}
        )
        self.assertEqual(response.status_code, 200)

        error_response = self.c.post(
            '/vocabularies/{0}/prefixes'.format(self.vocabulary.name),
            {'prefixes': 'error'}
        )
        self.assertEqual(error_response.status_code, 400)

    # settings view tests
    def test_settings_view(self):
        get = self.c.get(
            '/vocabularies/{0}/settings'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, 'vocabulary_setting.html')

    def test_set_review(self):
        response = self.c.post(
            '/vocabularies/{0}/settings'.format(self.vocabulary.name),
            {'vocabulary-setting': 'Review'}
        )
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertEqual(voc.state, 'Review')
        self.assertEqual(response.status_code, 200)

    def test_set_live(self):
        response = self.c.post(
            '/vocabularies/{0}/settings'.format(self.vocabulary.name),
            {'vocabulary-setting': 'Live'}
        )
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertEqual(voc.state, 'Live')
        self.assertEqual(response.status_code, 200)

    def test_set_dev(self):
        response = self.c.post(
            '/vocabularies/{0}/settings'.format(self.vocabulary.name),
            {'vocabulary-setting': 'Development'}
        )
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertEqual(voc.state, 'Development')
        self.assertEqual(response.status_code, 200)

    def test_settings_delete(self):
        set_dev = self.c.post(
            '/vocabularies/{0}/settings'.format(self.vocabulary.name),
            {'delete': ''}
        )
        self.assertEqual(set_dev.status_code, 302)

    # members view tests
    def test_members_view(self):
        get_response = self.c.get(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get_response, "vocabulary_members.html")

    def test_invite_user(self):
        test_user = User.objects.create(
            username='member@example.com', email='member@example.com')
        test_user.profile.name = 'member'
        test_user.save()
        response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'invite': '', 'email': 'member@example.com'},
            follow=True
        )
        self.assertContains(response, 'member@example.com')
        self.assertRedirects(
            response, '/vocabularies/{0}/members'.format(self.vocabulary.name))
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertTrue(voc.profiles.filter(user=test_user).exists())

        # invite same user again
        error_response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'invite': '', 'email': 'member@example.com'},
            follow=True
        )
        self.assertEquals(error_response.content, b'already in Vocabulary')

    def test_invite_and_kick_group(self):
        response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'invite': '', 'email': 'hey'},
            follow=True
        )
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertContains(response, 'hey')
        self.assertRedirects(
            response, '/vocabularies/{0}/members'.format(self.vocabulary.name))
        self.assertTrue(voc.groups.filter(vocabulary=voc).exists())

        # invite same group again
        error_response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'invite': '', 'email': 'hey'},
            follow=True
        )
        self.assertEquals(error_response.content, b'already in Vocabulary')

        kick_response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'kick-member': 'hey', 'type': 'GroupProfile'},
            follow=True
        )
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertFalse(voc.groups.filter(vocabulary=voc).exists())

    def test_invite_user_or_group_does_not_exist(self):
        response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'invite': '', 'email': 'error'},
            follow=True
        )
        self.assertEqual(response.status_code, 404)

    def test_kick_self(self):
        response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'kick-member': 'jhon@example.com', 'type': 'Profile'},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_kick_member(self):
        # add member
        test_user = User.objects.create(
            username='member@example.com', email='member@example.com')
        test_user.profile.name = 'member'
        test_user.save()
        self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'invite': '', 'email': 'member@example.com'},
            follow=True
        )
        kick_response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'kick-member': 'member@example.com', 'type': 'Profile'},
            follow=True
        )
        self.assertEqual(kick_response.status_code, 200)
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertFalse(voc.groups.filter(vocabulary=voc).exists())

    def test_kickall(self):
        response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'kickall': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_change_user_permission(self):
        # invite user
        test_user = User.objects.create(
            username='member@example.com', email='member@example.com')
        test_user.profile.name = 'member'
        test_user.save()
        self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'invite': '', 'email': 'member@example.com'},
            follow=True
        )
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertTrue('participant' in get_perms(test_user, voc))

        # change role
        response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'role': 'owner', 'nameormail': 'member@example.com', 'type': 'Profile'},
            follow=True
        )
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertFalse('participant' in get_perms(test_user, voc))
        self.assertTrue('owner' in get_perms(test_user, voc))

    # overview functionality tests

    def test_overview_view(self):
        get = self.c.get(
            '/vocabularies/{0}'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, "vocabulary.html")

    def test_overview_comment(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'comment': '', 'comment-text': 'Example comment'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Example comment')
        self.assertTrue(Comment.objects.filter(
            text='Example comment').exists())

    def test_overview_add_and_delete_tag(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'tag': '', 'tag-name': 'Example tag'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Tag.objects.filter(name='Example tag').exists())

        delete_response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'delete-tag': 'Example tag'},
            follow=True
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Tag.objects.filter(name='Example tag').exists())

    def test_create_literal_property(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'literal', 'object': 'example label'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'skos:note')
        self.assertContains(response, 'example label')

        get_response = self.c.get(
            '/vocabularies/{0}'.format(self.vocabulary.name),
        )

    def test_create_uri_property(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'uri', 'object': 'https://github.com/'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'skos:note')
        self.assertContains(response, 'https://github.com/')

    def test_create_property_empty_predicate(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'type': 'uri', 'object': 'abc'},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_empty_object(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note', 'type': 'uri'},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_invalid_uri(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'uri', 'object': 'abc'},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_is_not_valid_uri(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'uri', 'object': 'wa wa wa wa'},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_literal_invalid(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'literal', 'object': "'''"},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_create_property_valid_lang(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'literal', 'object': 'testproperty', 'language': 'en'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'skos:note')
        self.assertContains(response, 'testproperty')
        self.assertContains(response, 'en')

    def test_create_property_invalid_lang(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'type': 'literal', 'object': 'testproperty', 'language': 'error'},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_edit_uri_field(self):
        # create field
        self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'obj-type': 'uri', 'object': 'https://github.com/'},
        )
        # edit field
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
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
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'obj-type': 'literal', 'object': 'example label'},
        )

        # edit field
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
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
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'obj-type': 'uri', 'object': 'https://github.com/'},
        )
        # edit field
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'obj': 'https://github.com/', 'key': 'skos:note', 'lang': '',
                'new-obj': 'error', 'obj-type': 'uri', 'obj-datatype': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_edit_literal_field_invalid_literal(self):
        # create field
        self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'obj-type': 'literal', 'object': 'example label'},
        )

        # edit field
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'obj': 'example label', 'key': 'skos:note', 'lang': '',
                'new-obj': "'''", 'obj-type': 'literal', 'obj-datatype': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_field(self):
        # create field
        self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note',
                'obj-type': 'literal', 'object': 'example label', 'lang': 'en'},
        )

        # delete field
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'obj': 'example label', 'key': 'skos:note', 'lang': 'en',
                'new-obj': '', 'obj-type': 'literal', 'obj-datatype': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_download_ttl(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'download': 'turtle'},
        )
        self.assertEqual('{0}'.format(
            response), '<HttpResponse status_code=200, \"application/ttl\">')
        self.assertEqual(response.status_code, 200)

    def test_download_jsonld(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'download': 'json-ld'},
        )
        self.assertEqual('{0}'.format(
            response), '<HttpResponse status_code=200, \"application/json-ld\">')
        self.assertEqual(response.status_code, 200)

    def test_download_rdfxml(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'download': 'rdf+xml'},
        )
        self.assertEqual('{0}'.format(
            response), '<HttpResponse status_code=200, \"application/rdf+xml\">')
        self.assertEqual(response.status_code, 200)

    def test_overview_search(self):
        # create term so that search finds something
        self.c.post(
            '/vocabularies/{0}/terms'.format(self.vocabulary.name),
            {'create-term': '', 'term-subject': 'testterm', 'term-label': 'testlabel'}
        )

        response = self.c.get(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'search': 'test'},
        )
        self.assertContains(response, 'test')

    def test_terms_view(self):
        get = self.c.get(
            '/vocabularies/{0}/terms'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, "vocabulary_terms.html")

    def test_terms_view_add_term(self):
        term_subject = 'term123'
        object = '\'\'\'{0}\'\'\''.format('apfel')
        urispace = '<{0}{1}>'.format(
            self.vocabulary.urispace, term_subject.rstrip())
        predicate = '<http://www.w3.org/2004/02/skos/core#prefLabel>'
        self.vocabulary.create_field(urispace, predicate, object)
        self.vocabulary.create_field(urispace, '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>',
                                '<http://www.w3.org/2004/02/skos/core#Concept>')

        self.vocabulary.add_term(term_subject, term_subject)
        get = self.c.get(
            '/vocabularies/{0}/terms'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, "vocabulary_terms.html")

    def test_create_term(self):
        response = self.c.post(
            '/vocabularies/{0}/terms'.format(self.vocabulary.name),
            {'create-term': '', 'term-subject': 'testterm', 'term-label': 'testlabel'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertTrue(voc.term_set.filter(name='testterm').exists())

        # create same term again
        error_response = self.c.post(
            '/vocabularies/{0}/terms'.format(self.vocabulary.name),
            {'create-term': '', 'term-subject': 'testterm', 'term-label': 'testlabel'}
        )
        self.assertEqual(error_response.status_code, 409)

    # base view tests

    def test_base_view(self):
        get = self.c.get(
            '/vocabularies/'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, "base.html")

    def test_create_vocabulary(self):
        response = self.c.post(
            '/vocabularies/',
            {'create-vocabulary': '', 'name': 'example',
                'urispace': 'https://github.com/'}
        )
        self.assertTrue(Vocabulary.objects.filter(name='example').exists())
        self.assertRedirects(response, '/vocabularies/')
        voc = Vocabulary.objects.get(name='example')
        fuseki_dev.delete_vocabulary(voc)
        voc.delete()

    def test_create_vocabulary_invalid_form(self):
        response = self.c.post(
            '/vocabularies/',
            {'create-vocabulary': ''}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_vocabulary_invalid_form_bad_name(self):
        response = self.c.post(
            '/vocabularies/',
            {'create-vocabulary': '', 'name': 'example',
                'urispace': ''}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_vocabulary_invalid_form_bad_urispace(self):
        response = self.c.post(
            '/vocabularies/',
            {'create-vocabulary': '', 'name': 'example',
                'urispace': 'localhost:8080'}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_vocabulary_already_exists(self):
        response = self.c.post(
            '/vocabularies/',
            {'create-vocabulary': '', 'name': 'genel',
                'urispace': 'https://github.com/'}
        )
        self.assertEqual(response.status_code, 409)

    def test_base_search(self):
        # create term so that search finds something
        self.c.post(
            '/vocabularies/{0}/terms'.format(self.vocabulary.name),
            {'create-term': '', 'term-subject': 'testterm', 'term-label': 'testlabel'}
        )

        response = self.c.get(
            '/vocabularies/'.format(self.vocabulary.name),
            {'search': 'test'},
            follow=True
        )
        self.assertContains(response, 'test')

    def test_create_vocabulary_ttl_import(self):
        with open('tests/iptc-skos.ttl', 'rb') as ttl:
            response = self.c.post(
                '/vocabularies/',
                {'create-vocabulary': '', 'name': 'genel-ttl', 'file-upload': ttl},
                follow=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vocabulary.objects.filter(name='genel-ttl').exists())
        voc = Vocabulary.objects.get(name='genel-ttl')
        fuseki_dev.delete_vocabulary(voc)
        voc.delete()

    def test_create_vocabulary_txt_import(self):
        with open('tests/iptc-skos.txt', 'rb') as ttl:
            response = self.c.post(
                '/vocabularies/',
                {'create-vocabulary': '', 'name': 'genel-ttl',
                    'urispace': 'http://example.com', 'file-upload': ttl},
                follow=True
            )
        self.assertEqual(response.status_code, 400)

    def test_create_vocabulary_rdf_import(self):
        with open('tests/iptc-skos.rdf', 'rb') as rdf:
            response = self.c.post(
                '/vocabularies/',
                {'create-vocabulary': '', 'name': 'genel-rdf',
                    'urispace': 'http://example.com/', 'file-upload': rdf},
                follow=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vocabulary.objects.filter(name='genel-rdf').exists())
        voc = Vocabulary.objects.get(name='genel-rdf')
        fuseki_dev.delete_vocabulary(voc)
        voc.delete()

    def test_create_vocabulary_jsonld_import(self):
        with open('tests/testvoc.jsonld', 'rb') as jsonld:
            response = self.c.post(
                '/vocabularies/',
                {'create-vocabulary': '', 'name': 'genel-jsonld',
                    'urispace': 'http://cv.iptc.org/newscodes/', 'file-upload': jsonld},
                follow=True
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Vocabulary.objects.filter(
            name='genel-jsonld').exists())
        voc = Vocabulary.objects.get(name='genel-jsonld')
        fuseki_dev.delete_vocabulary(voc)
        voc.delete()

    def test_create_vocabulary_invalid_import(self):
        with open('tests/fail.ttl', 'rb') as fail:
            response = self.c.post(
                '/vocabularies/',
                {'create-vocabulary': '', 'name': 'genel-fail',
                    'urispace': 'http://example.com/', 'file-upload': fail},
                follow=True
            )
        self.assertEqual(response.status_code, 400)
