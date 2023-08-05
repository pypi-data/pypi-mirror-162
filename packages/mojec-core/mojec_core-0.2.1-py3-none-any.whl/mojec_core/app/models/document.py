from django.db import models

from .user import User
from .work_order import WorkOrder
from .base import BaseModelAbstract


class Documentation(BaseModelAbstract, models.Model):
    url = models.URLField(blank=True, null=True)
    user = models.ForeignKey(User, models.SET_NULL,
                             blank=True, null=True, 
                             related_name="documentations")

    class Meta:
        db_table = 'Documentations'


class Document(BaseModelAbstract, models.Model):
    workOrder = models.ForeignKey(WorkOrder, models.SET_NULL,
                                  blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    filename = models.CharField(db_column='fileName', max_length=255,
                                blank=True, null=True)
    type = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'Documents'
