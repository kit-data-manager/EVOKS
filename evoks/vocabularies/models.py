from django.db import models

# Create your models here.

class Vocabulary(models.Model):
    description = models.CharField(max_length=30)
    term_count = models.IntegerField()