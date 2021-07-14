from django.db import models
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

class GroupProfile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, blank=True)
    #group_owner = User
    size = models.IntegerField(default=1)
    

    @receiver(post_save, sender=Group)
    def create_groupprofile(sender, instance, created, **kwargs):
        if created:
            GroupProfile.objects.create(group=instance)

    @receiver(post_save, sender=Group)
    def save_groupprofile(sender, instance, **kwargs):
        instance.groupprofile.save()

    def add_user(self,User):
        self.group.user_set.add(User)
        self.size = self.size + 1
        self.group.save()
