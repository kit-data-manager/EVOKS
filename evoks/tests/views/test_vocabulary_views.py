from django.test import TestCase
from django.test import Client
from unittest import skip

from django.contrib.auth.models import User, Group
from vocabularies.models import Vocabulary
from evoks.fuseki import fuseki_dev


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
        self.vocabulary = Vocabulary.create(name='genel', urispace='http://www.testurispace.de', creator=self.user.profile)
        self.c = Client()
        self.c.login(username='jhon@example.com', password='ok')

    @classmethod
    def tearDown(self):
        try:
            fuseki_dev.delete_vocabulary(self.vocabulary)
        except:  # will fail when running the test_settings_delete testcase
            pass

    def test_prefix_view(self):
        get = self.c.get(
            '/vocabularies/{0}/prefixes'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, "vocabulary_prefixes.html")
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

    def test_settings_view(self):
        get = self.c.get(
            '/vocabularies/{0}/settings'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, "vocabulary_setting.html")

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


    def test_members_view(self):
        get_response = self.c.get(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get_response, "vocabulary_members.html")

    def test_invite_user(self):
        test_user = User.objects.create(
            username='member@example.com', email='member@example.com')
        test_user.profile.name = 'member'
        response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'invite': '', 'email': 'member@example.com'},
            follow=True
        )
        self.assertContains(response, 'member@example.com')
        self.assertRedirects(response, '/vocabularies/{0}/members'.format(self.vocabulary.name))
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertTrue(voc.profiles.filter(user=test_user).exists())
    
    def test_invite_and_kick_group(self):
        Group.objects.create(name='hey')
        response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'invite': '', 'email': 'hey'},
            follow=True
        )
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertContains(response, 'hey')
        self.assertRedirects(response, '/vocabularies/{0}/members'.format(self.vocabulary.name))
        self.assertTrue(voc.groups.filter(vocabulary=voc).exists())

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

    def test_kick_member(self):
        response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'kick-member': 'jhon@example.com', 'type': 'Profile'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_kickall(self):
        response = self.c.post(
            '/vocabularies/{0}/members'.format(self.vocabulary.name),
            {'kickall': ''},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_base_view(self):
        get = self.c.get(
            '/vocabularies/'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, "base.html")

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
        #TODO test

    def test_overview_add_and_delete_tag(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'tag': '', 'tag-name': 'Example tag'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        #TODO test

        delete_response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'delete-tag': 'Example tag'},
            follow=True
        )
        #TODO test

    @skip('doesnt work yet')
    def test_create_property(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note', 'type': 'literal', 'object': 'example label'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        #TODO test


    def test_download_ttl(self):
        #TODO test
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'download': 'turtle'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
    
    def test_download_jsonld(self):
        #TODO test
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'download': 'json-ld'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_download_rdfxml(self):
        #TODO test
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'download': 'rdf+xml'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_terms_view(self):
        get = self.c.get(
            '/vocabularies/{0}/terms'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, "vocabulary_terms.html")