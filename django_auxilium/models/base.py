"""
Collection of simple abstract base models with a few additional attributes
which don't require much logic.
"""

from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    """
    This model adds date created and last date modified attributes

    Attributes
    ----------
    created : DateTime
        The datetime when the model instance is created
    modified : DateTime
        The datetime when the model was last modified and saved
    """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta(object):
        abstract = True


class UserModel(models.Model):
    """
    This model adds a foreign key to a user attribute

    Attributes
    ----------
    user : User
        The user associated with the model
    """
    user = models.ForeignKey(User)

    class Meta(object):
        abstract = True
