from django.db import models

from .base import BaseModelAbstract
from .user import User


class VerificationType(BaseModelAbstract, models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'VerificationTypes'


class Verification(BaseModelAbstract, models.Model):
    type = models.ForeignKey(VerificationType, models.SET_NULL,
                             blank=True, null=True)
    user = models.ForeignKey(User, models.SET_NULL, blank=True, null=True, 
                             related_name="verifications")
    username = models.CharField(db_column='userName', max_length=255,
                                blank=True, null=True)
    meansOfIdentificationId = models.IntegerField(
        db_column='meansOfIdentificationId', blank=True, null=True
    )
    meansOfIdentificationName = models.CharField(
        db_column='meansOfIdentificationName', max_length=255, blank=True,
        null=True
    )
    active = models.BooleanField(default=False)

    class Meta:
        db_table = 'Verifications'




