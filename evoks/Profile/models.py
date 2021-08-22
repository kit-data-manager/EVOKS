from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from io import BytesIO
from zipfile import ZipFile
from django.core.mail import EmailMessage


class Profile(models.Model):
    """
    Profile model with one-to-one relation to user model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, blank=True)
    name = models.TextField(max_length=50, blank=False)
    verified = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        """
        creates  profile if user is created. use User.objects.create()
        """
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        """
        save_user_profile automatically saves profile if User is saved. use user.save()
        """
        instance.profile.save()

    def verify(self) -> None:
        """
        verify sets verified in profile true
        """
        self.verified = True
        self.user.save()

    def export_data(self) -> None:
        """
        sends a mail with the userdata to the user
        """
        # in memory zipfile
        in_memory = BytesIO()

        zip = ZipFile(in_memory, 'a')
        # add basic info to zip
        zip.writestr('data.txt', 'email: {0} \nname: {1}\ndescription: {2}'.format(
            self.user.email, self.name, self.description))
        zip.close()

        email = EmailMessage(subject='userdata from evoks', to=[
                             self.user.email], body='your userdata from evoks', from_email=settings.EVOKS_MAIL)
        email.attach('data.zip', in_memory.getvalue(), 'application/zip')
        email.send()
