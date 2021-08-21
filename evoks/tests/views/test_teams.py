from django.test import TestCase
from django.test import Client
from unittest import skip

from django.contrib.auth.models import User, Group


class Teams_test(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Set up non-modified objects used by all test methods
        cls.user = User.objects.create(
            username='jhon@example.com', email='jhon@example.com')
        cls.user.set_password('ok')
        cls.user.profile.verify()
        cls.user.save()
        cls.c=Client()
        cls.c.login(username='jhon@example.com', password='ok')
    
    def test_open_teamlist(self):
        response = self.c.get(
            '/teams'
        )
        self.assertTemplateUsed(response, "teams.html")

    def test_create_group(self):
        self.c.post('/teams', {'create-team': '','team-name' : 'team1'})
        response=self.c.get('/teams/team1')
        self.assertTemplateUsed(response, "team_detail.html")

    def test_create_group2(self):
        self.c.post('/teams', {'create-team': '','team-name' : 'team1'})
        response=self.c.post('/teams', {'create-team': '','team-name' : 'team1'})
        self.assertEqual(response.content, b'already exists')
    
    def test_create_group_wrong(self):
        response=self.c.post('/teams', {'create-team': '','team-name' : ' '})
        self.assertEqual(response.content, b'no leading or ending space chracters')

    