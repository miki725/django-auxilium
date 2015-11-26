"""
Collection of simple abstract base models with a few additional attributes
which don't require much logic.
"""

from __future__ import print_function, unicode_literals

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


User = settings.AUTH_USER_MODEL


class CreatedModel(models.Model):
    """
    This model adds date created attribute

    Attributes
    ----------
    created : DateTimeField
        The datetime when the model instance is created
    """
    created = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        abstract = True


class ModifiedModel(models.Model):
    """
    This model adds the last date modified attribute

    Attributes
    ----------
    modified : DateTimeField
        The datetime when the model was last modified and saved
    """
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True


class BaseModel(CreatedModel, ModifiedModel):
    """
    This model adds date created and last date modified attributes
    """

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
    notes : TextField
        Text field for storing notes
    """
    notes = models.TextField(blank=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class TitleDescriptionModel(BaseModel):
    """
    This model adds a title and description fields

    Attributes
    ----------
    title : CharField
        Maximum length is 256 character
    description : TextField
    """
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
