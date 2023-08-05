import time

from django.db import models

from .base import BaseModelAbstract
from .disco import Disco, BusinessUnit


class MeterRequest(BaseModelAbstract, models.Model):
    disco = models.ForeignKey(Disco, models.SET_NULL,
                              blank=True, null=True)
    businessUnit = models.ForeignKey(BusinessUnit, models.SET_NULL,
                                     blank=True, null=True)
    quantity = models.IntegerField(default=1)
    phone = models.CharField(max_length=11, blank=True, null=True)
    account = models.CharField(max_length=255, blank=True, null=True)
    orderId = models.CharField(db_column='orderId', max_length=30,
                               blank=False, null=False)
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, default='new')

    class Meta:
        db_table = 'MeterRequests'

    def save(self, keep_deleted=False, **kwargs):
        if not self.orderId:
            self.orderId = str(time.time()).split('.')[0]
        super(MeterRequest, self).save(keep_deleted=keep_deleted, **kwargs)
