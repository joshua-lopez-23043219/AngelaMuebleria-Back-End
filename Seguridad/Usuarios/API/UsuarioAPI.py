from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from Seguridad.Usuarios.API.SerializerUsuario import SerializerUsuario
from Seguridad.Usuarios.models import Usuario


class UsuarioViewsSet (ModelViewSet):

    #permission_classes = [IsAuthenticated]
    queryset = Usuario.objects.all()
    serializer_class = SerializerUsuario

    @action(detail=False, methods=['get'], url_path='activar/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)')
    def activar(self, request, uidb64=None, token=None):
        try:
            # 1. Decodificamos el ID del usuario
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            user = None
        from django.http import HttpResponseRedirect
        
        # 2. Verificamos si el token es válido
        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True  # Activamos al usuario
            user.email_verificado = True
            user.save()
            # Redirigimos al frontend con un mensaje de éxito
            return HttpResponseRedirect("https://angelamuebleria.business/?activated=true")

        else:
            # Redirigimos al frontend con un mensaje de error
            return HttpResponseRedirect("https://angelamuebleria.business/?activated=false")