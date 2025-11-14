from django.apps import AppConfig


class GameModeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'game_mode'

    def ready(self):
        import game_mode.signals
