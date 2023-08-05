from django.contrib.auth.models import AbstractUser
from django.db import models

from .base import BaseModelAbstract


class User(AbstractUser, BaseModelAbstract):
    """
        Overrides django's default auth model
    """
    first_name = None
    last_name = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "username"]
    
    email = models.EmailField(unique=True, null=False, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    phoneNumber = models.CharField(
        db_column='phoneNumber', unique=True,
        max_length=11, blank=True, null=True)
    emailVerified = models.BooleanField(db_column='emailVerified', blank=True,
                                        null=True)
    phoneNumberVerified = models.BooleanField(db_column='phoneNumberVerified',
                                              blank=True,
                                              null=True)
    verified = models.BooleanField(blank=True, null=True)
    verificationMode = models.CharField(db_column='verificationMode',
                                        max_length=255, blank=True,
                                        null=True)
    platform = models.CharField(max_length=15, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    bankAccountNumber = models.CharField(db_column='bankAccountNumber',
                                         max_length=11, blank=True,
                                         null=True)  # Field name made
    isOnboardingComplete = models.BooleanField(
        db_column='isOnboardingComplete', default=False
    )
    onboardingStage = models.CharField(
        max_length=100,
        db_column='onboardingStage',
        blank=True, null=True
    )
    imageUrl = models.TextField(
        db_column='imageUrl', blank=True, null=True
    )
    bankAccountName = models.CharField(db_column='bankAccountName',
                                       max_length=255, blank=True,
                                       null=True)  # Field name made lowercase.
    bankCode = models.CharField(db_column='bankCode', max_length=10,
                                blank=True,
                                null=True)
    sbcId = models.UUIDField(blank=True, null=True)
    fcmToken = models.JSONField(
        db_column='fcmToken', blank=True, null=True
    )
    locationLatitude = models.FloatField(
        default=0
    )
    locationLongitude = models.FloatField(
        default=0
    )

    class Meta:
        db_table = 'Users'
