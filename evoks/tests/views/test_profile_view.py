from django.test import TestCase
from django.test import Client
from unittest import skip
from vocabularies.models import Vocabulary

from django.contrib.auth.models import User,Group
from evoks.fuseki import fuseki_dev
from evoks.settings import SKOSMOS_LIVE_URI, SKOSMOS_DEV_URI
from guardian.shortcuts import assign_perm, remove_perm, get_perms

class Teams_test(TestCase):
    @classmethod
    def setUp(cls) -> None:
        # Set up non-modified objects used by all test methods
        cls.user = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        cls.user.set_password('ok')
        cls.user.profile.verify()
        cls.user.save()

        cls.user2 = User.objects.create(
            username='jhon2@example.com', email='jhon2@example.com')
        cls.user2.set_password('ok')
        cls.user2.profile.verify()
        cls.user2.save()

        cls.c=Client()
        cls.c.login(username='jhon@example.com', password='ok')

    @classmethod
    def tearDown(cls) -> None:
        if Vocabulary.objects.filter(name='testvocabulary').exists():
            voc=Vocabulary.objects.get(name='testvocabulary')
            if voc.state == 'Review':
                skosmos_dev.delete_vocabulary(voc.name)
            fuseki_dev.delete_vocabulary(voc)
            voc.delete() 

        if Group.objects.filter(name='team1').exists():
            Group.objects.get(name='team1').delete()

        if User.objects.filter(email='jhon@example.com').exists():
            cls.user.delete()
        if User.objects.filter(email='jhon2@example.com').exists():
            cls.user2.delete()
        
        

    def test_delete(self):
        self.c.post('/profile', {'delete': ''})
        self.assertFalse(User.objects.filter(email='jhon@example.com').exists())

    def test_delete_in_empty_voc(self):
        self.c.post('/vocabularies', {'create-vocabulary': '', 'name':'testvocabulary','urispace':'a'})
        self.assertTrue(Vocabulary.objects.filter(name='testvocabulary').exists())
        self.c.post('/profile', {'delete': ''})
        self.assertFalse(Vocabulary.objects.filter(name='testvocabulary').exists())                        
    
    def test_delete_in_voc(self):
        self.c.post('/vocabularies', {'create-vocabulary': '', 'name':'testvocabulary','urispace':'a'})
        self.assertTrue(Vocabulary.objects.filter(name='testvocabulary').exists())
        self.c.post('/vocabularies/testvocabulary/members', {'invite':'','email':'jhon2@example.com'})
        self.c.post('/profile', {'delete': ''})
        voc=Vocabulary.objects.filter(name='testvocabulary')
        self.assertTrue(voc.exists())
        self.assertTrue( 'owner' in get_perms(self.user2, voc.first()))
    
    def test_delete_in_voc_with_group(self):
        self.c.post('/vocabularies', {'create-vocabulary': '', 'name':'testvocabulary','urispace':'a'})
        self.assertTrue(Vocabulary.objects.filter(name='testvocabulary').exists())
        self.c.post('/teams', {'create-team': '','team-name' : 'team1'})
        self.c.post('/teams/team1',{'email': 'jhon2@example.com', 'invite':''})
        self.c.post('/vocabularies/testvocabulary/members', {'invite':'','email':'team1'})
        self.c.post('/profile', {'delete': ''})
        voc=Vocabulary.objects.filter(name='testvocabulary')
        group=Group.objects.filter(name='team1')
        self.assertTrue(voc.exists())
        self.assertTrue( 'owner' in get_perms(group.first(), voc.first()))

    def test_delete_in_empty_group(self):
        self.c.post('/teams', {'create-team': '','team-name' : 'team1'})
        self.assertTrue(Group.objects.filter(name='team1').exists())
        self.c.post('/profile', {'delete': ''})
        self.assertFalse(Group.objects.filter(name='team1').exists())

    def test_delete_in_group(self):
        self.c.post('/teams', {'create-team': '','team-name' : 'team1'})
        self.assertTrue(Group.objects.filter(name='team1').exists())
        self.c.post('/teams/team1',{'email': 'jhon2@example.com', 'invite':''})
        self.c.post('/profile', {'delete': ''})
        self.assertTrue(Group.objects.filter(name='team1').exists())
        owner=Group.objects.get(name='team1').groupprofile.group_owner
        self.assertEqual(owner,self.user2)