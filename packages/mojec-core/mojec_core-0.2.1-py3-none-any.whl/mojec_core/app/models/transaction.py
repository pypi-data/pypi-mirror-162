from django.db import models

from .work_order import WorkOrder
from .base import BaseModelAbstract

TYPES = (
    ('wallet-topup', 'wallet-topup'),
    ('wallet-withdrawal', 'wallet-withdrawal'),
    ('kyc-verification', 'kyc-verification'),
    ('meter-vend', 'meter-vend'),
    ('buy-meter', 'buy-meter'),
    ('service-order-commitment', 'service-order-commitment'),
    ('service-order-complete', 'service-order-complete'),
    ('others', 'others'),
)


class TransactionLog(BaseModelAbstract, models.Model):
    transactionRef = models.CharField(unique=True, max_length=255)
    paymentRef = models.CharField(db_column='paymentRef', max_length=255,
                                  blank=True, null=True)
    paymentVendor = models.ForeignKey(
        "PaymentVendor", models.SET_NULL,
        blank=True, null=True)
    workOrder = models.ForeignKey(WorkOrder, models.SET_NULL,
                                  blank=True, null=True)
    platform = models.CharField(max_length=30, blank=True, null=True)
    requestJson = models.JSONField(
        db_column='requestJSON', blank=True, null=True)
    responseJson = models.JSONField(
        db_column='responseJSON', blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=15, default=0)
    isPaid = models.BooleanField(default=False) 
    status = models.CharField(max_length=30, blank=True, null=True)
    transactionType = models.CharField(max_length=30, choices=TYPES)
    vendorStatus = models.CharField(max_length=30, blank=True, null=True)
    callbackJson = models.JSONField(db_column='callbackJSON', blank=True, 
                                    null=True)  # Field name made lowercase.
    verifyJson = models.JSONField(db_column='verifyJSON', blank=True, 
                                  null=True)  # Field name made lowercase.
    webhookJson = models.JSONField(db_column='webhookJSON', blank=True, 
                                   null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'TransactionLogs'
