from django.db import models

from .base import BaseModelAbstract
from .user import User


class Conversation(BaseModelAbstract, models.Model):
    user1 = models.ForeignKey(
        User, models.SET_NULL, related_name="chat_user1_set",
        null=True, blank=True
    )
    user2 = models.ForeignKey(
        User, models.SET_NULL, related_name="chat_user2_set",
        null=True, blank=True
    )

    class Meta:
        db_table = 'Conversations'


class Message(BaseModelAbstract, models.Model):
    conversation = models.ForeignKey(Conversation, models.DO_NOTHING,
                                     blank=True, null=True,
                                     related_name="messages")
    sender = models.ForeignKey(User, models.SET_NULL, related_name="messages",
                               blank=True, null=True)
    message = models.TextField(blank=False, null=False)
    type = models.CharField(max_length=30, blank=False, null=False)

    class Meta:
        db_table = 'Messages'
