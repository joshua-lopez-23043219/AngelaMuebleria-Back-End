from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from APPS.Personalizacion.models import MuebleBase, ColorMaterial
from APPS.Personalizacion.API.SerializerPersonalizacion import SerializerMuebleBase, SerializerColorMaterial

from rest_framework.decorators import action

class MuebleBaseViewsSet(ModelViewSet):
    queryset = MuebleBase.objects.all()
    serializer_class = SerializerMuebleBase
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def debug_db(self, request):
        from django.conf import settings
        import os
        
        media_files = []
        try:
            media_root = settings.MEDIA_ROOT
            if os.path.exists(media_root):
                for root, dirs, files in os.walk(media_root):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), media_root)
                        media_files.append(rel_path)
            else:
                media_files = f"MEDIA_ROOT path {media_root} does not exist"
        except Exception as e:
            media_files = f"Error scanning media: {str(e)}"
            
        return Response({
            "databases": settings.DATABASES,
            "media_root": settings.MEDIA_ROOT,
            "media_files_found": media_files
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
