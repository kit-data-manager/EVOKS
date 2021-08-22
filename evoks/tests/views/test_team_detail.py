from django.test import TestCase
from django.test import Client
from unittest import skip

from django.contrib.auth.models import User, Group


class Team_detail_test(TestCase):
    @classmethod
    def setUpTestData(self) -> None:
        # Set up non-modified objects used by all test methods
        self.user_a = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        self.user_a.set_password('ok')
        self.user_a.profile.verify()
        self.user_a.save()
        self.user_b = User.objects.create(
            username='b@example.com', email='b@example.com')
        self.user_b.set_password('ok')
        self.user_b.profile.verify()
        self.user_b.save()
        self.c2 = Client()
        self.c = Client()
        self.c.login(username='jhon@example.com', password='ok')
        self.team1 = Group.objects.create(name='team1')
        self.team1.groupprofile.group_owner = self.user_a
        self.team1.groupprofile.add_user(self.user_a)
        self.team1.save()
        self.team2 = Group.objects.create(name='team2')
        self.team2.groupprofile.group_owner = self.user_b
        self.team2.groupprofile.add_user(self.user_a)
        self.team2.groupprofile.add_user(self.user_b)
        self.team2.save()

    def test_description(self):
        self.c.post('/teams/team1', {'description': 'hi', 'save': ''})
        team = Group.objects.get(name='team1')
        self.assertEqual(team.groupprofile.description, 'hi')

    def test_invite(self):
        self.c.post('/teams/team1', {'email': 'b@example.com', 'invite': ''})
        b = User.objects.get(email='b@example.com')
        self.assertTrue(b.groups.filter(name='team1').exists())

    def test_invite_second_time(self):
        self.c.post('/teams/team1', {'email': 'b@example.com', 'invite': ''})
        response = self.c.post(
            '/teams/team1', {'email': 'b@example.com', 'invite': ''})
        self.assertEqual(response.content, b'already in group')

    def test_invite_not_exists(self):
        response = self.c.post(
            '/teams/team1', {'email': 'ö@example.com', 'invite': ''})
        self.assertEqual(response.content, b'error: does not exist')

    def test_invite_size(self):
        self.c.post('/teams/team1', {'email': 'b@example.com', 'invite': ''})
        team = Group.objects.get(name='team1')
        self.assertEqual(team.groupprofile.size, 2)

    def test_kick(self):
        self.c.post('/teams/team1', {'email': 'b@example.com', 'invite': ''})
        self.c.post('/teams/team1', {'kick': 'b@example.com'})
        b = User.objects.get(email='b@example.com')
        self.assertFalse(b.groups.filter(name='team1').exists())

    def test_kick_owner(self):
        self.c.post('/teams/team1', {'email': 'b@example.com', 'invite': ''})
        response = self.c.post('/teams/team1', {'kick': 'jhon@example.com'})
        self.assertEqual(response.content, b'can\'t kick yourself')

    def test_kick_all_size(self):
        self.c.post('/teams/team1', {'email': 'b@example.com', 'invite': ''})
        self.c.post('/teams/team1', {'kick_all': ''})
        team = Group.objects.get(name='team1')
        self.assertEqual(self.team1.groupprofile.size, 1)

    def test_delete(self):
        self.c.post('/teams/team1', {'delete': ''})
        self.assertFalse(Group.objects.filter(name='team1').exists())

    def test_delete_redirekt(self):
        response = self.c.post('/teams/team1', {'delete': ''})
        self.assertRedirects(response, '/teams')

    def test_not_owner_delete(self):
        response = self.c.post('/teams/team2', {'delete': ''})
        self.assertEqual(response.content, b'insufficient permission')

    def test_not_owner_invite(self):
        response = self.c.post(
            '/teams/team2', {'email': 'b@example.com', 'invite': ''})
        self.assertEqual(response.content, b'insufficient permission')

    def test_not_owner_kick(self):
        response = self.c.post('/teams/team2', {'kick': 'b@example.com'})
        self.assertEqual(response.content, b'insufficient permission')

    def test_not_owner_kick_all(self):
        response = self.c.post('/teams/team2', {'kick_all': ''})
        self.assertEqual(response.content, b'insufficient permission')

    def test_not_in_group(self):
        self.c2.login(username='b@example.com', password='ok')
        response = self.c2.post('/teams/team1')
        self.assertEqual(response.content, b'insufficient permission')
