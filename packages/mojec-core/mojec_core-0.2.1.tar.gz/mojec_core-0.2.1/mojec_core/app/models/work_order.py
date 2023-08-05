import time

from django.db import models

from .user_address import UserAddress
from .base import BaseModelAbstract
from .user import User
from .work_order_service import WorkOrderServiceCategory
from .payment import PaymentVendor


class WorkOrder(BaseModelAbstract, models.Model):
    serviceSubCategory = models.ForeignKey(
        WorkOrderServiceCategory, models.SET_NULL,
        db_column='serviceSubCategory', blank=True, null=True)
    agent = models.ForeignKey(User, models.SET_NULL, blank=True, null=True,
                              related_name="workorders_agent_set")
    address = models.TextField()
    longitude = models.CharField(max_length=30, default="0")
    latitude = models.CharField(max_length=30, default="0")
    # paymentType = models.ForeignKey(PaymentType, models.SET_NULL, null=True,
    #                                 blank=True)
    paymentVendor = models.ForeignKey(PaymentVendor, models.SET_NULL,
                                      null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    orderId = models.CharField(db_column='orderId', max_length=30,
                               blank=False, null=False)
    assessmentReport = models.TextField(
        db_column='assessmentReport', blank=True, null=True)
    completionReport = models.TextField(
        db_column='completionReport', blank=True, null=True)
    transactionReference = models.TextField(
        db_column='transactionReference', blank=True, null=True,
        max_length=255
    )
    generalStatus = models.CharField(db_column='generalStatus', default='new',
                                     max_length=30)
    currentStatus = models.CharField(db_column='currentStatus',
                                     default='unAssigned', max_length=30)
    noteForAgent = models.TextField(db_column='noteForAgent', blank=True,
                                    null=True)
    additionalNote = models.TextField(db_column='additionalNote',
                                      blank=True, null=True)
    date = models.DateTimeField(blank=False, null=False)
    fee = models.DecimalField(max_digits=15, decimal_places=2,
                                     default=0)
    commission = models.DecimalField(max_digits=15, decimal_places=2,
                                     default=0)
    totalAmount = models.DecimalField(db_column='totalAmount',
                                      max_digits=15, decimal_places=2,
                                      default=0)
    actualServiceCharge = models.DecimalField(
        db_column='actualServiceCharge', max_digits=15, decimal_places=2,
        default=0)
    remainingtotalAmount = models.DecimalField(
        db_column='remainingtotalAmount', max_digits=15, decimal_places=2,
        default=0)
    totalMaterialsFee = models.DecimalField(db_column='totalMaterialsFee',
                                            max_digits=15, decimal_places=2,
                                            default=0)
    isCommitmentFeePaid = models.BooleanField(db_column='isCommitmentFeePaid',
                                              default=False)
    agentEnroute = models.BooleanField(db_column='agentEnroute',
                                       default=False)
    agentArrived = models.BooleanField(db_column='agentArrived',
                                       default=False)
    isAssessmentCompleted = models.BooleanField(
        db_column='isAssessmentCompleted',
        default=False
    )
    paymentCompleted = models.BooleanField(db_column='paymentCompleted',
                                           default=False)
    paymentCompletedAt = models.DateTimeField(db_column='paymentCompletedAt',
                                              blank=True, null=True)
    jobStartedAt = models.DateTimeField(db_column='jobStartedAt',
                                        blank=True, null=True)
    jobCompletedByAgentAt = models.DateTimeField(
        db_column='jobCompletedByAgentAt',
        blank=True, null=True)
    jobCompletedByCustomerAt = models.DateTimeField(
        db_column='jobCompletedByCustomerAt',
        blank=True, null=True)
    assessmentCompletedAt = models.DateTimeField(
        db_column='assessmentCompletedAt', blank=True, null=True)
    isAgentJobComplete = models.BooleanField(db_column='isAgentJobComplete',
                                             blank=True, null=True)
    customerCompletionConfirmation = models.BooleanField(
        db_column='customerCompletionConfirmation', default=False)
    isAgentReview = models.BooleanField(db_column='isAgentReview',
                                        default=False)
    isCustomerReview = models.BooleanField(
        db_column='isCustomerReview', default=False
    )
    agentEnrouteAt = models.DateTimeField(db_column='agentEnrouteAt',
                                          blank=True, null=True)
    agentArrivedAt = models.DateTimeField(db_column='agentArrivedAt',
                                          blank=True, null=True)
    agentAssignedAt = models.DateTimeField(db_column='agentAssignedAt',
                                           blank=True, null=True)

    def save(self, keep_deleted=False, **kwargs):
        if not self.orderId:
            self.orderId = str(time.time()).split('.')[0]
        super(WorkOrder, self).save(keep_deleted=keep_deleted, **kwargs)

    class Meta:
        db_table = 'WorkOrders'
