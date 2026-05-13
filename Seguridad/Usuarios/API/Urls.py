from rest_framework.routers import DefaultRouter

from Seguridad.Usuarios.API.SerializerUsuario import SerializerUsuario

routerUsuario = DefaultRouter()

routerUsuario.register(r'Usuario', SerializerUsuario ,basename='Usuario')