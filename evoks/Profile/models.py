from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    # delete TODO in one to one drinnen?
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, blank=True)
    name = models.TextField(max_length=50, blank=False)
    verified = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    # hier fehlt admin abfrage TODO

    def verify(self):
        self.verified = True
        self.user.save()

    # export TODO

    def export_userdata(self):
        # datei=open('daten.txt','a')
        # datei.write('hi') kreirt file muss aber auch wieder gelöscht oder überschrieben werde
        self.user.email_user(subject='Data', message='Ihre Daten bei Evoks'+self.name+'sind:'+self.description)
        #[self.user.email]