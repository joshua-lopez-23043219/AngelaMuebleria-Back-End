from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.ComboPedidos.API.SerializerComboPedido import SerializerComboPedido
from APPS.ComboPedidos.models import ComboPedido


class ComboPedidoViewsSet (ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = ComboPedido.objects.all()
    serializer_class = SerializerComboPedido



