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


class NoteModel(BaseModel):
    """
    This model adds a notes field

    Attributes
    ----------
    notes : str
    """
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True


class TitleDescriptionModel(BaseModel):
    """
    This model adds a notes field

    Attributes
    ----------
    title : str
        Maximum length is 256 character
    description : str
    """
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True
