from django.db import models
from django.db.models.deletion import CASCADE

# Create your models here.

class Term(models.Model):
    name = models.CharField(max_length=30, unique=True)
    vocabulary = models.ForeignKey(to='vocabularies.Vocabulary', on_delete=CASCADE, blank=True, null=True)

    @classmethod
    def create(cls, name : str):
        """Creates a Term

        Args:
            name (str): Name of the Term
        """
        term = cls(name=name)
        term.save()
        return term
