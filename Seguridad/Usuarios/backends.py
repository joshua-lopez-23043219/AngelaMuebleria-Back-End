from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Permite autenticar usando el username o el correo electrónico.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(Usuario.USERNAME_FIELD)
        
        # Intentamos buscar por email primero
        try:
            user = Usuario.objects.get(email=username)
        except Usuario.DoesNotExist:
            # Si no existe por email, intentamos por username
            try:
                user = Usuario.objects.get(username=username)
            except Usuario.DoesNotExist:
                # Si no existe de ninguna forma, llamamos a hash_password para evitar ataques de timing
                Usuario().set_password(password)
                return None
        
        # Verificamos la contraseña y si el usuario puede autenticarse
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
