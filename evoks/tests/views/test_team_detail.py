from django.test import TestCase
from django.test import Client
from unittest import skip

from django.contrib.auth.models import User, Group


class Team_detail_test(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Set up non-modified objects used by all test methods
        cls.user_a = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        cls.user_a.set_password('ok')
        cls.user_a.profile.verify()
        cls.user_a.save()
        cls.user_b = User.objects.create(
            username='b@example.com', email='b@example.com')
        cls.user_b.set_password('ok')
        cls.user_b.profile.verify()
        cls.user_b.save()
        cls.c2=Client()
        cls.c=Client()
        cls.c.login(username='jhon@example.com', password='ok')
        cls.team1= Group.objects.create(name='team1')
        cls.team1.groupprofile.group_owner=cls.user_a
        cls.team1.groupprofile.add_user(cls.user_a)
        cls.team1.save()
        cls.team2= Group.objects.create(name='team2')
        cls.team2.groupprofile.group_owner=cls.user_b
        cls.team2.groupprofile.add_user(cls.user_a)
        cls.team2.groupprofile.add_user(cls.user_b)
        cls.team2.save()
        
    def test_description(self):
        self.c.post('/teams/team1', {'description': 'hi' ,'save': ''})
        team=Group.objects.get(name='team1')
        self.assertEqual(team.groupprofile.description,'hi')

    def test_invite(self):
        self.c.post('/teams/team1',{'email': 'b@example.com', 'invite':''})
        b=User.objects.get(email='b@example.com')
        self.assertTrue(b.groups.filter(name='team1').exists())

    def test_invite_second_time(self):
        self.c.post('/teams/team1',{'email': 'b@example.com', 'invite':''})
        response=self.c.post('/teams/team1',{'email': 'b@example.com', 'invite':''})
        self.assertEqual(response.content,b'already in group')
    
    def test_invite_not_exists(self):
        response=self.c.post('/teams/team1',{'email': 'ö@example.com', 'invite':''})
        self.assertEqual(response.content,b'error: does not exist')

    def test_invite_size(self):
        self.c.post('/teams/team1',{'email': 'b@example.com', 'invite':''})
        team=Group.objects.get(name='team1')
        self.assertEqual(team.groupprofile.size,2)
    
    def test_kick_owner(self):
        self.c.post('/teams/team1',{'email': 'b@example.com', 'invite':''})
        self.c.post('/teams/team1',{'kick': 'b@example.com'})
        b=User.objects.get(email='b@example.com')
        self.assertFalse(b.groups.filter(name='team1').exists())
    
    def test_kick_owner(self):
        self.c.post('/teams/team1',{'email': 'b@example.com', 'invite':''})
        response=self.c.post('/teams/team1',{'kick': 'jhon@example.com'})
        self.assertEqual(response.content,b'can\'t kick yourself')

    def test_kick_all_size(self):
        self.c.post('/teams/team1',{'email': 'b@example.com', 'invite':''})
        self.c.post('/teams/team1',{'kick_all':''})
        team=Group.objects.get(name='team1')
        self.assertEqual(self.team1.groupprofile.size,1)

    def test_delete(self):
        self.c.post('/teams/team1',{'delete':''})
        self.assertFalse(Group.objects.filter(name='team1').exists())

    def test_delete_redirekt(self):
        response=self.c.post('/teams/team1',{'delete':''})
        self.assertRedirects(response, '/teams')

    def test_not_owner_delete(self):
        response=self.c.post('/teams/team2',{'delete':''})
        self.assertEqual(response.content,b'insufficient permission')
    
    def test_not_owner_invite(self):
        response=self.c.post('/teams/team2',{'email': 'b@example.com', 'invite':''})
        self.assertEqual(response.content,b'insufficient permission')
    
    def test_not_owner_kick(self):
        response=self.c.post('/teams/team2',{'kick': 'b@example.com'})
        self.assertEqual(response.content,b'insufficient permission')
    
    def test_not_owner_kick_all(self):
        response=self.c.post('/teams/team2',{'kick_all':''})
        self.assertEqual(response.content,b'insufficient permission')
    
    def test_not_in_group(self):
        self.c2.login(username='b@example.com', password='ok')
        response=self.c2.post('/teams/team1')
        self.assertEqual(response.content,b'insufficient permission')