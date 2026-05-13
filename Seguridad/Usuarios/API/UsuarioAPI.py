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



