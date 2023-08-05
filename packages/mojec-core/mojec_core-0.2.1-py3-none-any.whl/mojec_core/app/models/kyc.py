from django.db import models

from .disco import BusinessUnit
from .base import BaseModelAbstract
from .user import User


class Kyc(BaseModelAbstract, models.Model):
    createdBy = models.OneToOneField(User, on_delete=models.CASCADE,
                                     related_name='kyc')
    employerName = models.CharField(db_column='employerName', max_length=255,
                                    blank=True, null=True)
    dateOfBirth = models.DateField(null=False, blank=False)
    country = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    placeOfWork = models.TextField(db_column='placeOfWork', blank=True,
                                   null=True)
    officeAddress = models.TextField(db_column='landlordAddress',
                                     blank=True, null=True)
    landlordName = models.CharField(db_column='landlordName', max_length=255)
    bvn = models.CharField(max_length=11, blank=True, null=True)
    postCode = models.CharField(max_length=50, blank=True, null=True)
    accountNumber = models.CharField(max_length=50)
    undertaking = models.CharField(max_length=150, blank=True, null=True)
    transformer = models.CharField(max_length=150, blank=True, null=True)
    accountType = models.CharField(db_column='accountType', max_length=30)
    idNumber = models.CharField(db_column='idNumber', max_length=30)
    idType = models.CharField(db_column='idType', max_length=150,
                              blank=True, null=True)
    feeder = models.CharField(max_length=255, null=True, blank=True)
    tariffClass = models.CharField(max_length=255, null=True, blank=True)
    businessUnit = models.ForeignKey(BusinessUnit, models.SET_NULL,
                                     null=True)
