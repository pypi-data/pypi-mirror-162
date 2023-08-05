from django.db import models
from .base import BaseModelAbstract


class PaymentVendor(BaseModelAbstract, models.Model):
    type = models.CharField(max_length=30, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    accountNo = models.CharField(db_column='accountNo', max_length=255,
                                 blank=True, null=True)
    accountName = models.CharField(db_column='accountName',
                                   max_length=255, blank=True, null=True)
    ref = models.CharField(max_length=30, blank=True, null=True)
    logo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'PaymentVendors'

#
# class Payment(BaseModelAbstract, models.Model):
#     orderId = models.CharField(db_column='orderId', max_length=255,
#                                blank=True,
#                                null=True)  # Field name made lowercase.
#     transactionRef = models.CharField(
#         db_column='transactionRef', max_length=255, blank=True, null=True)
#     paymentRef = models.CharField(db_column='paymentRef', max_length=255,
#                                   blank=True, null=True)
#     transactionLog = models.ForeignKey(TransactionLog, models.SET_NULL,
#                                        blank=True, null=True)
#     paymentVendor = models.ForeignKey(PaymentVendor, models.SET_NULL,
#                                       blank=True, null=True)
#     # paymentType = models.ForeignKey(PaymentType, models.SET_NULL,
#     #                                 blank=True, null=True)
#     paymentJson = models.JSONField(db_column='paymentJSON', blank=True,
#                                    null=True)  # Field name made lowercase.
#     channel = models.CharField(max_length=255, blank=True, null=True)
#
#     class Meta:
#         db_table = 'Payments'
#
