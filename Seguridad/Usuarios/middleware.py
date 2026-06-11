from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from Seguridad.Usuarios.models import Usuario

class ActualizarUltimaActividadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check standard session authentication first
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            Usuario.objects.filter(pk=request.user.pk).update(ultima_actividad=timezone.now())
        else:
            # Try to authenticate using JWT if header is present (REST API requests from frontend client)
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                try:
                    authenticator = JWTAuthentication()
                    auth_result = authenticator.authenticate(request)
                    if auth_result:
                        user, _ = auth_result
                        if user and user.is_authenticated:
                            Usuario.objects.filter(pk=user.pk).update(ultima_actividad=timezone.now())
                except Exception:
                    pass
        
        response = self.get_response(request)
        return response
