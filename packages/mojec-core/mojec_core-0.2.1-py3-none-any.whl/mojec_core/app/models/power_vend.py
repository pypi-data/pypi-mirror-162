from django.db import models
from mojec_core.app.models import BaseModelAbstract


class PowerVend(BaseModelAbstract, models.Model):
    meter_number = models.CharField(max_length=250)
    red_code = models.CharField(max_length=250)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=30, default='new', blank=True,
                              null=True)
    token = models.CharField(max_length=250)
    action = models.CharField(max_length=250)

    class Meta:
        db_table = 'PowerVend'
