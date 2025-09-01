from django.db import models


class State(models.TextChoices):
    """State TextChoices that represent the state of the Vocabulary

    Args:
        models (TextChoices): possible states of a vocabulary
    """
    DEV = 'Development'
    REVIEW = 'Review'
    LIVE = 'Live'