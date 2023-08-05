from django.db import models

from .base import BaseModelAbstract


class Disco(BaseModelAbstract, models.Model):
    longName = models.CharField(max_length=255, blank=False, null=False)
    shortName = models.CharField(max_length=10, blank=False, null=False)
    location = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'Discos'


class BusinessUnit(BaseModelAbstract, models.Model):
    disco = models.ForeignKey(Disco, models.CASCADE,
                              related_name="business_units")
    name = models.CharField(max_length=255, blank=False, null=False)
    location = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'BusinessUnits'
