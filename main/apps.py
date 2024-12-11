from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        from main.config.user_agency_patch import install_user_agency_patch
        install_user_agency_patch()
