from django.db import models
from .base import BaseModelAbstract
from .payment import PaymentVendor


class Card(BaseModelAbstract, models.Model):
    signature = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    paymentVendor = models.ForeignKey(PaymentVendor,
                                      on_delete=models.SET_NULL,
                                      null=True, blank=True)
    authorization = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'Cards'

# {
#     "bin": "408408",
#     "bank": "TEST BANK",
#     "brand": "visa",
#     "last4": "4081",
#     "channel": "card",
#     "exp_year": "2030",
#     "reusable": true,
#     "card_type": "visa ",
#     "exp_month": "12",
#     "signature": "SIG_QkKdsx2GPbL6GMLAx7Og",
#     "account_name": null,
#     "country_code": "NG",
#     "authorization_code": "AUTH_c5ad99qtsf"
# }
