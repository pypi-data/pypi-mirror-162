from django.db import models

from .base import BaseModelAbstract
from .cart import Cart
from .product import Product


class Purchase(BaseModelAbstract, models.Model):
    cart = models.ForeignKey(Cart, models.SET_NULL,
                             blank=True, null=True)
    product = models.ForeignKey(Product, models.SET_NULL,
                                blank=True, null=True)
    quantity = models.IntegerField(default=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=30, default='pending', blank=True, 
                              null=True)

    class Meta:
        db_table = 'Purchases'
