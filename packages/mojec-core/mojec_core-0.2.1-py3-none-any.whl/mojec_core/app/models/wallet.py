from django.db import models

from .work_order import WorkOrder
from .transaction import TransactionLog
from .base import BaseModelAbstract
from .user import User


class Wallet(BaseModelAbstract, models.Model):
    createdBy = None
    user = models.OneToOneField(User, models.CASCADE, null=False, 
                                blank=False, related_name="wallet")
    balance = models.DecimalField(default=0, max_digits=15, decimal_places=2)

    class Meta:
        db_table = 'Wallets'


TYPES = (
    ("earnings", "earnings"),
    ("deposit", "deposit"),
    ("withdrawal", "withdrawal"),
    ("payment", "payment"),
)


class WalletHistory(BaseModelAbstract, models.Model):
    workOrder = models.ForeignKey(WorkOrder, models.SET_NULL,
                                  blank=True, null=True)
    transactionLog = models.ForeignKey(TransactionLog, models.SET_NULL,
                                       blank=True, null=True)
    wallet = models.ForeignKey(Wallet, models.SET_NULL, blank=True, null=True)
    amount = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    balanceBefore = models.DecimalField(default=0, max_digits=15,
                                        decimal_places=2)
    balanceAfter = models.DecimalField(default=0, max_digits=15,
                                       decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=30, choices=TYPES, blank=True,
                            null=True)
    isSuccessful = models.BooleanField(db_column='isSuccessful', default=False)

    class Meta:
        db_table = 'WalletHistories'
