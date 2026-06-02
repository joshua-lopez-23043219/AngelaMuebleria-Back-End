from django.utils import timezone
from Seguridad.Usuarios.models import Usuario

class ActualizarUltimaActividadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user and request.user.is_authenticated:
            # Efficiently update the last activity timestamp in the DB without full save()
            Usuario.objects.filter(pk=request.user.pk).update(ultima_actividad=timezone.now())
        
        response = self.get_response(request)
        return response
