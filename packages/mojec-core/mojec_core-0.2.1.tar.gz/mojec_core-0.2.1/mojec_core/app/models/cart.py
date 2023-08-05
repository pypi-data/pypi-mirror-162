from django.db import models
from .base import BaseModelAbstract


class Cart(BaseModelAbstract, models.Model):
    totalAmount = models.DecimalField(db_column='totalAmount',
                                      max_digits=15, decimal_places=2,
                                      default=0)
    status = models.TextField(blank=True, null=True)
    transactionRef = models.CharField(db_column='transactionRef',
                                      max_length=255, blank=True,
                                      null=True)
    deliveryAddress = models.TextField(db_column='deliveryAddress',
                                       blank=True, null=True)

    class Meta:
        db_table = 'Carts'

