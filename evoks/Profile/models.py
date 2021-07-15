from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, blank=True)
    name = models.TextField(max_length=50, blank=False)
    verified = models.BooleanField(default=False)

    """
    creates  profile if user is created. use User.objects.create()
    """
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    """
    save_user_profile automatically saves profile if User is saved. use user.save
    """
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    """
    verify sets verified in profile true
    """
    def verify(self):
        self.verified = True
        self.user.save()

    """
    export_userdata sends a mail with userdata to the mail from user.email
    """
    def export_userdata(self):
        self.user.email_user(subject='Data', message='Ihre Daten bei Evoks'+self.name+'sind:'+self.description)
        