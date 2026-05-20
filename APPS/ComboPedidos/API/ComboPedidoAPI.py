from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.ComboPedidos.API.SerializerComboPedido import SerializerComboPedido, SerializerReglaCombo
from APPS.ComboPedidos.models import ComboPedido, ReglaCombo


class IsAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or (hasattr(request.user, 'rol') and request.user.rol == 'admin')
        )


class ComboPedidoViewsSet (ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = ComboPedido.objects.all()
    serializer_class = SerializerComboPedido


class ReglaComboViewsSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = ReglaCombo.objects.all().order_by('-creado_en')
    serializer_class = SerializerReglaCombo




