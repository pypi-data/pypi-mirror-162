from django.db import models

from .base import BaseModelAbstract


class MeansOfIdentification(BaseModelAbstract, models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'MeansOfIdentifications'


