from django.db import models

from .base import BaseModelAbstract
from .user import User


class UserAddress(BaseModelAbstract, models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    text = models.TextField(null=False, blank=False)
