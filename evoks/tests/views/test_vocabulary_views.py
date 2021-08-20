from django.test import TestCase
from django.test import Client
from unittest import skip

from django.contrib.auth.models import User, Group
from vocabularies.models import Vocabulary
from Term.models import Term
from evoks.fuseki import fuseki_dev
from evoks.skosmos import skosmos_dev, skosmos_live


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
        self.group = Group.objects.create(name='hey')

    @classmethod
    def tearDown(self):
        #skosmos_dev.delete_vocabulary(self.vocabulary.name)
        try:
            fuseki_dev.delete_vocabulary(self.vocabulary)

        except:  # will fail when running the test_settings_delete testcase
            pass

        #skosmos_live.delete_vocabulary('{0}-{1}'.format(self.vocabulary.name, self.vocabulary.version - 1))

    #prefix view tests
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

    #settings view tests
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

    @skip('doesnt work yet')
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

    #members view tests
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
        self.assertRedirects(response, '/vocabularies/{0}/members'.format(self.vocabulary.name))
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertTrue(voc.profiles.filter(user=test_user).exists())

        #invite same user again
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
        self.assertRedirects(response, '/vocabularies/{0}/members'.format(self.vocabulary.name))
        self.assertTrue(voc.groups.filter(vocabulary=voc).exists())

        #invite same group again
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

    #overview functionality tests
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

    def test_overview_add_and_delete_tag(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'tag': '', 'tag-name': 'Example tag'},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Example tag')

        delete_response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'delete-tag': 'Example tag'},
            follow=True
        )
        self.assertNotContains(delete_response, 'Example tag')
        self.assertEqual(delete_response.status_code, 200)

    def test_create_literal_property(self):
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note', 'type': 'literal', 'object': 'example label'},
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
            {'create-property': '', 'predicate': 'skos:note', 'type': 'uri', 'object': 'https://github.com/'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'skos:note')
        self.assertContains(response, 'https://github.com/')

    def test_edit_uri_field(self):
        #create field
        self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note', 'type': 'uri', 'object': 'https://github.com/'},
        )

        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'obj': 'https://github.com/', 'key': 'skos:note', 'lang': '', 'new-obj': 'https://gitlab.com/', 'obj-type': 'uri'},
            follow=True
        )
        print(response.status_code)
        #self.assertNotContains(response, 'https://github.com/')
        self.assertContains(response, 'skos:note')
        #self.assertContains(response, 'https://gitlab.com/')

    def test_edit_literal_field(self):
        #create field
        self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'create-property': '', 'predicate': 'skos:note', 'type': 'literal', 'object': 'example label'},
        )

        #edit field
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'obj': 'example label', 'key': 'skos:note', 'lang': '', 'new-obj': 'example field', 'obj-type': 'literal'},
            follow=True
        )
        print(response.status_code)
        #self.assertNotContains(response, 'example label')
        self.assertContains(response, 'skos:note')
        #self.assertContains(response, 'example field')




    def test_download_ttl(self):
        #TODO test
        response = self.c.post(
            '/vocabularies/{0}'.format(self.vocabulary.name),
            {'download': 'turtle'},
            follow=True
        )
        print(response.context)
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

    def test_create_term(self):
        response = self.c.post(
            '/vocabularies/{0}/terms'.format(self.vocabulary.name),
            {'create-term': '', 'term-name': 'testterm', 'term-label': 'testlabel'}
        )
        self.assertEqual(response.status_code, 200)
        voc = Vocabulary.objects.get(name=self.vocabulary.name)
        self.assertTrue(voc.term_set.filter(name='testterm').exists())

        #create same term again
        error_response = self.c.post(
            '/vocabularies/{0}/terms'.format(self.vocabulary.name),
            {'create-term': '', 'term-name': 'testterm', 'term-label': 'testlabel'}
        )
        self.assertEqual(error_response.content, b'Term with this name already exists')
        self.assertEqual(error_response.status_code, 409)

        get_response = self.c.get(
            '/vocabularies/{0}/terms'.format(self.vocabulary.name),
        )

    #base view tests
    def test_base_view(self):
        get = self.c.get(
            '/vocabularies/'.format(self.vocabulary.name),
        )
        self.assertTemplateUsed(get, "base.html")

    def test_create_vocabulary(self):
        response = self.c.post(
            '/vocabularies/',
            {'create-vocabulary': '', 'name': 'example', 'urispace': 'https://github.com/'}
        )
        self.assertTrue(Vocabulary.objects.filter(name='example').exists())
        self.assertRedirects(response, '/vocabularies/'.format(self.vocabulary.name))
        voc = Vocabulary.objects.get(name='example')
        fuseki_dev.delete_vocabulary(voc)
        voc.delete()
    
    def test_create_vocabulary_invalid_form(self):
        response = self.c.post(
            '/vocabularies/',
            {'create-vocabulary': ''}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Invalid form')

    def test_create_vocabulary_already_exists(self):
        response = self.c.post(
            '/vocabularies/',
            {'create-vocabulary': '', 'name': 'genel', 'urispace': 'https://github.com/'}
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.content, b'vocabulary already exists')

    def test_dashboard(self):
        self.vocabulary.set_review()
        self.vocabulary.add_group(self.group.groupprofile, 'participant')
        self.group.groupprofile.add_user(self.user)
        get_response = self.c.get(
            '/vocabularies/',
        )
        #TODO test

    def test_create_vocabulary_ttl_import(self):
        with open('iptc-skos.ttl', 'rb') as fp:
            self.c.post(
                '/vocabularies/',
                {'create-vocabulary': '', 'name': 'genel-ttl', 'urispace': 'http://cv.iptc.org/newscodes/', 'file-upload': fp}
            )
            
        self.assertTrue(Vocabulary.objects.get(name='genel-ttl').exists())
        voc = Vocabulary.objects.get(name='genel-ttl')
        fuseki_dev.delete_vocabulary(voc)
        voc.delete()

    @skip('functionality in different branch')
    def test_create_vocabulary_rdf_import(self):
        with open('iptc-skos.rdf', 'rb') as fp:
            response = self.c.post(
                '/vocabularies/',
                {'create-vocabulary': '', 'name': 'genel-rdf', 'urispace': 'http://cv.iptc.org/newscodes/', 'file-upload': fp}
            )
        
        self.assertTrue(Vocabulary.objects.filter(name='genel-rdf').exists())
        voc = Vocabulary.objects.get(name='genel-rdf')
        fuseki_dev.delete_vocabulary(voc)
        voc.delete()

    @skip('functionality in different branch')    
    def test_create_vocabulary_jsonld_import(self):
        with open('testvoc.jsonld', 'rb') as fp:
            response = self.c.post(
                '/vocabularies/', 
                {'create-vocabulary': '', 'name': 'genel-jsonld', 'urispace': 'http://www.yso.fi/onto/yso/', 'file-upload': fp}
            )
            
        self.assertTrue(Vocabulary.objects.get(name='genel-jsonld').exists())
        voc = Vocabulary.objects.get(name='genel-jsonld')
        fuseki_dev.delete_vocabulary(voc)
        voc.delete()
    
    @skip('functionality in different branch')
    def test_create_vocabulary_invalid_import(self):
        with open('fail.ttl', 'rb') as fp:
            response = self.c.post(
                '/vocabularies/',
                {'create-vocabulary': '', 'name': 'genel-fail', 'urispace': 'http://example.com/', 'file-upload': fp},
                follow=True
            )

        #voc = Vocabulary.objects.get(name='genel-fail')
        #fuseki_dev.delete_vocabulary(voc)
        #voc.delete()
        self.assertEqual(response.status_code, 409)