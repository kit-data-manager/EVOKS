from django.db import models
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class GroupProfile(models.Model):
    """
    Group profile with one-to-one relation to a group.
    """
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, blank=True)
    size = models.IntegerField(default=1)

    @receiver(post_save, sender=Group)
    def create_groupprofile(sender, instance, created, **kwargs):
        if created:
            GroupProfile.objects.create(group=instance)

    @receiver(post_save, sender=Group)
    def save_groupprofile(sender, instance, **kwargs):
        instance.groupprofile.save()

    def add_user(self, user: User) -> None:
        """Adds user to the group

        Args:
            user (User): user to be added to group
        """
        self.group.user_set.add(user)
        self.size = self.size + 1
        self.group.save()

    def remove_user(self, user: User) -> None:
        """Removes user from group

        Args:
            user (User): user to be removed from group
        """
        self.group.user_set.remove(user)
        self.size = self.size - 1
        if self.size < 1:
            self.group.delete()
        else:
            self.group.save()
