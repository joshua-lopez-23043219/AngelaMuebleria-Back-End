from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.Pedidos.API.SerializerPedidos import SerializerPedidos
from APPS.Pedidos.models import Pedido


class PedidosViewsSet (ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = Pedido.objects.all()
    serializer_class = SerializerPedidos



