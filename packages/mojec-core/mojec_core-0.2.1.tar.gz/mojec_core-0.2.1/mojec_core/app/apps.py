from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'mojec_core.app'
