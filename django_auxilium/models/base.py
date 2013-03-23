"""
Collection of simple abstract base models with a few additional attributes
which don't require much logic.
"""

from __future__ import unicode_literals, print_function
from django.db import models, IntegrityError
from django.contrib.auth.models import User
from uuid import uuid4


class CreatedModel(models.Model):
    """
    This model adds date created attribute

    Attributes
    ----------
    created : DateTime
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
    modified : DateTime
        The datetime when the model was last modified and saved
    """
    modified = models.DateTimeField(auto_now_add=True, auto_now=True)

    class Meta(object):
        abstract = True


class BaseModel(CreatedModel, ModifiedModel):
    """
    This model adds date created and last date modified attributes.
    Inherits from ``CreatedModel`` and ``ModifiedModel``.
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

    def __unicode__(self):
        return self.title


class UUIDModel(models.Model):
    uuid = models.CharField(max_length=32, blank=True, unique=True)

    class Meta:
        abstract = True

    def generate_uuid(self, force=False):
        if not self.uuid or force:
            self.uuid = uuid4().get_hex()

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.generate_uuid()

        if kwargs.pop('assure_unique_uuid', True):
            while True:
                try:
                    return super(UUIDModel, self).save(*args, **kwargs)
                except IntegrityError:
                    self.generate_uuid(True)
        else:
            return super(UUIDModel, self).save(*args, **kwargs)
