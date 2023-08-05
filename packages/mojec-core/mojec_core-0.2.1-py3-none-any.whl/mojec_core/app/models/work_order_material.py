from django.db import models

from . import Product
from .work_order import WorkOrder
from .base import BaseModelAbstract


class WorkOrderMaterial(BaseModelAbstract, models.Model):
    workOrder = models.ForeignKey(WorkOrder, on_delete=models.SET_NULL,
                                  null=True, blank=True)
    product = models.ForeignKey(Product, null=True, blank=True,
                                on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        db_table = 'WorkOrderMaterials'

