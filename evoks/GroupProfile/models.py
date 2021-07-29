from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class GroupProfile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(max_length=500, blank=True)
    group_owner = models.OneToOneField(User, on_delete=models.PROTECT,null=True)
    size = models.IntegerField(default=1)

    
    @receiver(post_save, sender=Group)
    def create_groupprofile(sender, instance, created, **kwargs):
        """
        creates Profile when User is created. use: User.objects.create()
        """
        if created:
            GroupProfile.objects.create(group=instance)

    
    @receiver(post_save, sender=Group)
    def save_groupprofile(sender, instance, **kwargs):
        """
        saves when matching user saves. use: user.save()
        """
        instance.groupprofile.save()

    

    def add_user(self, user:User):
        """
        add_user adds a user to the group and counts groupsize up.
        """
        self.group.user_set.add(user)
        self.size = self.size + 1
        self.group.save()

    

    def remove_user(self, user:User):
        """ 
        remove_user removes the given user and counts groupsize down.
        deletes the group if no user remains.
        """
        self.group.user_set.remove(user)
        self.size = self.size - 1  
        self.group.save()     
        if self.size < 1:
            Group.objects.get(id=self.group.id).delete()
            
        
