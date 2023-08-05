from django.db import models

from .base import BaseModelAbstract
from .user import User


class NextOfKin(BaseModelAbstract, models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True, 
                             related_name="nextofkins")
    address = models.CharField(max_length=255, blank=True, null=True)
    relationship = models.CharField(max_length=30, blank=False, null=False)
    phoneNumber = models.CharField(db_column='phoneNumber', max_length=11,
                                   blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'NextOfKins'
