from django.db import models

# Create your models here.


class Vocabulary(models.Model):
    description = models.CharField(max_length=30, default='')
    term_count = models.IntegerField(default=0)
    name = models.CharField(max_length=30, default='')

    def get_name(self):
        return self.name
