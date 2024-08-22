from unittest.case import skip
from Profile.models import Profile
from logging import PlaceHolder
from django.test import TestCase
from vocabularies.models import Vocabulary, State, Dataformat
from GroupProfile.models import GroupProfile
from django.contrib.auth.models import User, Group
from Term.models import Term
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from evoks.fuseki import fuseki_dev
from evoks.skosmos import skosmos_live, skosmos_dev


class VocabularyTest(TestCase):

    @classmethod
    def setUp(self):
        self.user = User.objects.create(username='jhon', password='ok',
                                        email='someone@example.com')
        self.vocabulary = Vocabulary.create(
            name='example', urispace='example.com/', creator=self.user.profile)
        self.vocabulary.prefixes = [
            'PREFIX xls: <http://xmlns.com/foaf/0.1/>', 'PREFIX pls: <http://plmns.com/foaf/0.1/>']

    @classmethod
    def tearDown(self):
        try:
            skosmos_dev.delete_vocabulary(self.vocabulary.name_with_version())
            skosmos_live.delete_vocabulary(self.vocabulary.name_with_version())
            fuseki_dev.delete_vocabulary(self.vocabulary)
        except:
            pass

    def test_create(self):
        vocabulary = self.vocabulary
        user = self.user

        # test creator assigned as owner
        self.assertEqual(vocabulary.profiles.get(user=user), user.profile)
        self.assertTrue(user.has_perm('owner', vocabulary))

        # test vocabulary state
        self.assertEqual(vocabulary.state, State.DEV)
        self.assertIsInstance(vocabulary, Vocabulary)

    def test_name_with_version(self):
        vocabulary = self.vocabulary
        name_with_version = vocabulary.name_with_version()
        self.assertEqual(name_with_version, 'example-1')

    def test_get_name(self):
        vocabulary = self.vocabulary
        self.assertEquals(vocabulary.get_name(), 'example')

    def test_validate_prefixes(self):
        vocabulary = self.vocabulary
        prefixes = vocabulary.prefixes
        self.assertFalse(vocabulary.validate_prefixes(['test']))
        self.assertFalse(vocabulary.validate_prefixes(['test test test']))
        self.assertTrue(vocabulary.validate_prefixes(prefixes))

    def test_validate_prefixes_invalid_prefix(self):
        vocabulary = self.vocabulary
        self.assertFalse(vocabulary.validate_prefixes(
            ['PREFIX invalid: <http://goo>.com>']))

    def test_get_namespaces(self):
        vocabulary = self.vocabulary
        namespaces = vocabulary.get_namespaces()
        self.assertCountEqual(namespaces,
                              [('skos', 'http://www.w3.org/2004/02/skos/core#'), ('dc', 'http://purl.org/dc/elements/1.1/'), ('dct', 'http://purl.org/dc/terms/'), ('xls', 'http://xmlns.com/foaf/0.1/'), ('pls', 'http://plmns.com/foaf/0.1/'), ('brick', 'https://brickschema.org/schema/Brick#'), ('csvw', 'http://www.w3.org/ns/csvw#'), ('dc', 'http://purl.org/dc/elements/1.1/'), ('dcat', 'http://www.w3.org/ns/dcat#'), ('dcmitype', 'http://purl.org/dc/dcmitype/'), ('dcterms', 'http://purl.org/dc/terms/'), ('dcam', 'http://purl.org/dc/dcam/'), ('doap', 'http://usefulinc.com/ns/doap#'), ('foaf', 'http://xmlns.com/foaf/0.1/'), ('geo', 'http://www.opengis.net/ont/geosparql#'), ('odrl', 'http://www.w3.org/ns/odrl/2/'), ('org', 'http://www.w3.org/ns/org#'), ('prof', 'http://www.w3.org/ns/dx/prof/'), ('prov', 'http://www.w3.org/ns/prov#'), ('qb', 'http://purl.org/linked-data/cube#'), ('schema', 'https://schema.org/'), ('sh', 'http://www.w3.org/ns/shacl#'), ('skos', 'http://www.w3.org/2004/02/skos/core#'), ('sosa', 'http://www.w3.org/ns/sosa/'), ('ssn', 'http://www.w3.org/ns/ssn/'), ('time', 'http://www.w3.org/2006/time#'), ('vann', 'http://purl.org/vocab/vann/'), ('void', 'http://rdfs.org/ns/void#'), ('wgs', 'https://www.w3.org/2003/01/geo/wgs84_pos#'), ('owl', 'http://www.w3.org/2002/07/owl#'), ('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'), ('rdfs', 'http://www.w3.org/2000/01/rdf-schema#'), ('xsd', 'http://www.w3.org/2001/XMLSchema#'), ('xml', 'http://www.w3.org/XML/1998/namespace')])

    def test_prefixes_to_str(self):
        vocabulary = self.vocabulary
        namespaces = vocabulary.get_namespaces()
        prefixes = vocabulary.prefixes_to_str(namespaces)

        self.assertEqual(prefixes, """prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix dct: <http://purl.org/dc/terms/>
prefix xls: <http://xmlns.com/foaf/0.1/>
prefix pls: <http://plmns.com/foaf/0.1/>
prefix brick: <https://brickschema.org/schema/Brick#>
prefix csvw: <http://www.w3.org/ns/csvw#>
prefix dc: <http://purl.org/dc/elements/1.1/>
prefix dcat: <http://www.w3.org/ns/dcat#>
prefix dcmitype: <http://purl.org/dc/dcmitype/>
prefix dcterms: <http://purl.org/dc/terms/>
prefix dcam: <http://purl.org/dc/dcam/>
prefix doap: <http://usefulinc.com/ns/doap#>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix geo: <http://www.opengis.net/ont/geosparql#>
prefix odrl: <http://www.w3.org/ns/odrl/2/>
prefix org: <http://www.w3.org/ns/org#>
prefix prof: <http://www.w3.org/ns/dx/prof/>
prefix prov: <http://www.w3.org/ns/prov#>
prefix qb: <http://purl.org/linked-data/cube#>
prefix schema: <https://schema.org/>
prefix sh: <http://www.w3.org/ns/shacl#>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
prefix sosa: <http://www.w3.org/ns/sosa/>
prefix ssn: <http://www.w3.org/ns/ssn/>
prefix time: <http://www.w3.org/2006/time#>
prefix vann: <http://purl.org/vocab/vann/>
prefix void: <http://rdfs.org/ns/void#>
prefix wgs: <https://www.w3.org/2003/01/geo/wgs84_pos#>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix xsd: <http://www.w3.org/2001/XMLSchema#>
prefix xml: <http://www.w3.org/XML/1998/namespace>""")


    def test_split_prefixes(self):
        vocabulary = self.vocabulary
        split_prefixes = vocabulary.split_prefixes(
            vocabulary.convert_prefixes(vocabulary.prefixes))
        self.assertEqual(split_prefixes, [
                         ('xls', 'http://xmlns.com/foaf/0.1/'), ('pls', 'http://plmns.com/foaf/0.1/')])

    def test_convert_prefixes(self):
        vocabulary = self.vocabulary
        converted = vocabulary.convert_prefixes(vocabulary.prefixes)
        self.assertEqual(converted, [
                         'PREFIX xls <http://xmlns.com/foaf/0.1/>', 'PREFIX pls <http://plmns.com/foaf/0.1/>'])

    def test_convert_prefix(self):
        vocabulary = self.vocabulary
        valid, uri = vocabulary.convert_prefix('skos:prefLabel')
        self.assertTrue(valid)
        self.assertEqual(uri, 'http://www.w3.org/2004/02/skos/core#prefLabel')

    def test_convert_prefix_invalid_namespace(self):
        vocabulary = self.vocabulary
        valid, uri = vocabulary.convert_prefix('WHAT:prefLabel')
        self.assertFalse(valid)

    def test_set_dev(self):
        vocabulary = self.vocabulary
        self.assertEqual(vocabulary.state, State.DEV)
        vocabulary.set_review()
        self.assertNotEqual(vocabulary.state, State.DEV)
        vocabulary.set_dev()
        self.assertEqual(vocabulary.state, State.DEV)

    def test_add_and_remove_term(self):
        # add term and test that its added afterwards
        vocabulary = self.vocabulary
        vocabulary.add_term(name='test', uri='cool/123')
        self.assertTrue(vocabulary.term_set.filter(name='test').exists())
        self.assertIsInstance(vocabulary.term_set.get(name='test'), Term)

        # remove term
        vocabulary.remove_term(name='test')
        # term no longer exists
        self.assertFalse(Term.objects.filter(name='test').exists())

    def test_add_and_remove_profile(self):
        # add profile
        vocabulary = self.vocabulary
        user = User.objects.create(username='bob', password='ok',
                                   email='bob@example.com')
        vocabulary.add_profile(user.profile, 'spectator')
        self.assertEqual(vocabulary.profiles.get(user=user), user.profile)
        self.assertIsInstance(vocabulary.profiles.get(user=user), Profile)
        self.assertTrue(user.has_perm('spectator', vocabulary))

        # remove profile
        vocabulary.remove_profile(user.profile)
        self.assertFalse(vocabulary.profiles.filter(user=user).exists())
        self.assertFalse(user.has_perm('spectator', vocabulary))

    def test_add_and_remove_group(self):
        vocabulary = self.vocabulary
        group = Group.objects.create(name='ontologische Ontologen')
        user = User.objects.create(username='bob', password='ok',
                                   email='bob@example.com')
        group.user_set.add(user)
        checker = ObjectPermissionChecker(group)
        # add group
        vocabulary.add_group(group.groupprofile, 'participant')
        self.assertTrue(vocabulary.groups.filter(group=group).exists())
        self.assertEqual(vocabulary.groups.get(
            group=group), group.groupprofile)
        self.assertTrue(checker.has_perm('participant', vocabulary))
        # remove group
        vocabulary.remove_group(group.groupprofile)
        # test group no longer part of vocabulary
        self.assertFalse(vocabulary.groups.filter(group=group).exists())

        # test group no longer has permission
        checker = ObjectPermissionChecker(group)
        self.assertFalse(checker.has_perm('participant', vocabulary))
