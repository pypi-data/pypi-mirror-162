from django.db import models
from .base import BaseModelAbstract
from .work_order import WorkOrder


class WorkOrderStatus(BaseModelAbstract, models.Model):
    workOrder = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    status = models.CharField(max_length=50, blank=True, null=True)
    currentStatus = models.BooleanField(
        db_column='currentStatus', default=True
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'WorkOrderStatuses'
