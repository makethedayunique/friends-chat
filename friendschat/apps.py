from django.apps import AppConfig


class FriendschatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'friendschat'

    def ready(self) -> None:
        import friendschat.signals