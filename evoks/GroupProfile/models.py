from django.db import models
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class GroupProfile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, blank=True)
    group_owner = models.IntegerField(default=1)
    size = models.IntegerField(default=1)

    """
    creates Profile when User is created. use: User.objects.create()
    """
    @receiver(post_save, sender=Group)
    def create_groupprofile(sender, instance, created, **kwargs):
        if created:
            GroupProfile.objects.create(group=instance)

    """
    saves when matching user saves. use: user.save()
    """
    @receiver(post_save, sender=Group)
    def save_groupprofile(sender, instance, **kwargs):
        instance.groupprofile.save()

    """
    add_user adds a user to the group and counts groupsize up.
    """

    def add_user(self, User):
        self.group.user_set.add(User)
        self.size = self.size + 1
        self.group.save()

    """ 
    remove_user removes the given user and counts groupsize down.
    deletes the group if no user remains.
    """

    def remove_user(self, User):
        self.group.user_set.remove(User)
        self.size = self.size - 1  
        self.group.save()     
        if self.size < 1:
            Group.objects.get(id=self.group.id).delete()
            
        
