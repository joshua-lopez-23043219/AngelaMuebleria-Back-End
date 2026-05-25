from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from APPS.Personalizacion.models import MuebleBase, ColorMaterial
from APPS.Personalizacion.API.SerializerPersonalizacion import SerializerMuebleBase, SerializerColorMaterial

class MuebleBaseViewsSet(ModelViewSet):
    queryset = MuebleBase.objects.all()
    serializer_class = SerializerMuebleBase
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def debug_db(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = list(User.objects.values('id', 'username', 'email', 'rol', 'is_superuser', 'is_staff', 'is_active'))
        return Response({
            "users": users
        })

    def create(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous or request.user.rol != 'admin':
            return Response({"error": "No tienes permisos de administrador para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous or request.user.rol != 'admin':
            return Response({"error": "No tienes permisos de administrador para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous or request.user.rol != 'admin':
            return Response({"error": "No tienes permisos de administrador para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

class ColorMaterialViewsSet(ModelViewSet):
    queryset = ColorMaterial.objects.all()
    serializer_class = SerializerColorMaterial
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous or request.user.rol != 'admin':
            return Response({"error": "No tienes permisos de administrador para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous or request.user.rol != 'admin':
            return Response({"error": "No tienes permisos de administrador para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous or request.user.rol != 'admin':
            return Response({"error": "No tienes permisos de administrador para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
