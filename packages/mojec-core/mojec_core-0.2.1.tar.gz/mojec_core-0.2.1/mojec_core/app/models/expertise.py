from django.db import models
from .base import BaseModelAbstract
from .user import User


class Expertise(BaseModelAbstract, models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    user = models.ForeignKey(User, models.SET_NULL,
                             blank=True, null=True, related_name="expertises")

    class Meta:
        db_table = 'Expertises'


