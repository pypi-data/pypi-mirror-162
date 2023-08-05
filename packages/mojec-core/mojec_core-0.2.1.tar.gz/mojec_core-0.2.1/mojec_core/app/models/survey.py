from django.db import models

from .base import BaseModelAbstract
from .work_order import WorkOrder


class Survey(BaseModelAbstract, models.Model):
    workOrder = models.ForeignKey(WorkOrder, models.SET_NULL,
                                  blank=True, null=True)
    responseTime = models.IntegerField(db_column='responseTime', default=0)
    professionalism = models.IntegerField(default=0)
    serviceQuality = models.IntegerField(db_column='serviceQuality',
                                         default=0)
    review = models.TextField(blank=True, null=True)
    rating = models.IntegerField(default=0)

    class Meta:
        db_table = 'Surveys'


