from rest_framework.routers import DefaultRouter

from Seguridad.Usuarios.API.SerializerUsuario import SerializerUsuario
from Seguridad.Usuarios.API.UsuarioAPI import UsuarioViewsSet

routerUsuario = DefaultRouter()

routerUsuario.register(r'Usuario', UsuarioViewsSet ,basename='Usuario')