from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    describtion = models.TextField(max_length=500, blank=True)
    name = models.TextField(max_length=50, blank=False)
    verified = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    # delete TODO in one to one drinnen?

    # hier fehlt admin abfrage TODO

    def verify(self):
        self.verified = True
        self.user.save()

    # export TODO

    def export_userdata(self):
        User.email_user(self, subject, 'Ihre Daten')
