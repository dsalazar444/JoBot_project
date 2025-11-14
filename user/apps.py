from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'
    
    def ready(self): 
        import user.signals #Para que una vez se active django, se importe el trigger y este pendiente al momento en que se cree un nuevo usuario
