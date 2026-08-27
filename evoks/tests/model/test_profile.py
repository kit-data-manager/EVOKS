from django.test import TestCase

from django.contrib.auth.models import User
from Profile.models import Profile, users_registered_gauge
from django.conf import settings
from unittest import skip
from prometheus_client import generate_latest


class ProfileTest(TestCase):
    @classmethod
    def setUp(self):
        # Set up non-modified objects used by all test methods
        self.user = User.objects.create(username='jhon', password='ok',
                                        email='example@example.de')

    @classmethod
    def tearDown(self):
        self.user.delete()

    def test_name(self):
        self.user.profile.name = 'tom'
        self.assertEquals(self.user.profile.name, 'tom')

    def test_verified_false(self):
        self.assertFalse(self.user.profile.verified)

    def test_verified_true(self):
        self.user.profile.verify()
        self.assertTrue(self.user.profile.verified)

    def test_description(self):
        self.user.profile.description = 'hi'
        self.user.save()
        self.assertEquals(self.user.profile.description, 'hi')


class RegisteredUsersMetricTest(TestCase):

    def test_gauge_matches_user_counts(self):
        User.objects.create(
            username='metric@example.com', password='ok',
            email='metric@example.com')
        verified = User.objects.filter(profile__verified=True).count()
        unverified = User.objects.filter(profile__verified=False).count()
        samples = {s.labels.get('user_verified'): s.value
                   for s in users_registered_gauge.collect()[0].samples}
        self.assertEqual(len(samples), 2)
        self.assertEqual(samples['true'], float(verified))
        self.assertEqual(samples['false'], float(unverified))

    def test_gauge_is_exposed_in_metrics_output(self):
        output = generate_latest()
        self.assertIn(b'evoks_users_registered{user_verified="true"}', output)
        self.assertIn(b'evoks_users_registered{user_verified="false"}', output)
