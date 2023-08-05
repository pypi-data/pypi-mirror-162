from django.db import models

from mojec_core.app.models import User

SERVICES = (
    ("msh", "msh"),
    ("payment", "payment"),
    ("inventory", "inventory"),
    ("customer", "customer"),
)


class Config(models.Model):
    service = models.CharField(max_length=50, choices=SERVICES, null=False)
    key = models.CharField(max_length=50, null=False, unique=True)
    value = models.CharField(max_length=100, null=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, models.SET_NULL,
                                        null=True, blank=True)

    def __str__(self):
        return f"{self.key}: {self.value}"
