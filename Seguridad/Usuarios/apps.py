from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Seguridad.Usuarios'

    # ESTE ES EL CAMBIO: La función ready()
    def ready(self):
        # Cuando la app Usuarios arranque, importa las señales para activarlas
        import Seguridad.Usuarios.Signal  # noqa
