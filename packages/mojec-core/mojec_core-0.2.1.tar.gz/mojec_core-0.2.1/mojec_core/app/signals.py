from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .managers.config_manager import ConfigManager
from .models import Config

__all__ = ['config_update_hook', 'config_delete_hook']


@receiver(post_save, sender=Config)
def config_update_hook(sender, instance, **kwargs):
    config_manager = ConfigManager(instance.service)
    config_manager.store(instance.key, instance.value)


@receiver(post_delete, sender=Config)
def config_delete_hook(sender, instance, **kwargs):
    config_manager = ConfigManager(instance.service)
    config_manager.delete(instance.key, instance.value)
