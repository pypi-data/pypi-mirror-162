import uuid
from django.conf import settings
from django.db import models
from safedelete.models import SafeDeleteModel
from django.utils import timezone


class BaseModelAbstract(SafeDeleteModel):
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    createdBy = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL,
                                  blank=True, null=True)
    
    deleted = models.BooleanField(default=False)
    deletedById = models.UUIDField(blank=True, null=True)
    
    deletedAt = models.DateTimeField(db_column='deletedAt', blank=True,
                                     null=True)
    createdAt = models.DateTimeField(db_column='createdAt',
                                     auto_now_add=True)
    updatedAt = models.DateTimeField(db_column='updatedAt', auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ('-createdAt', )
    
    def save(self, keep_deleted=False, **kwargs):
        if self.uid is None:
            self.uid = uuid.uuid4()
        super(BaseModelAbstract, self).save(keep_deleted, **kwargs)

    def delete(self, by=None, force_policy=None, **kwargs):
        self.deletedBy = by
        self.deleted = True
        super(BaseModelAbstract, self).delete(force_policy, **kwargs)

    def undelete(self, force_policy=None, **kwargs):
        self.deletedBy = None
        self.deleted = False
        super(BaseModelAbstract, self).undelete(force_policy, **kwargs)


# class BaseModel(BaseModelAbstract, models.Model):
#     pass
