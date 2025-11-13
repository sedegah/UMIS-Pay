from django.apps import AppConfig


class SerialgeneratorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'serialgenerator'

    def ready(self):
        import serialgenerator.signals
        return super().ready()
