from django.db import models

from .base import BaseModelAbstract


class Product(BaseModelAbstract, models.Model):
    productName = models.CharField(max_length=255,
                                   blank=False, null=False)
    description = models.CharField(max_length=255, blank=False, null=False)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=30, default='active', blank=True, 
                              null=True)

    class Meta:
        db_table = 'Products'
