from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.Categoria.API.SerializerCategoria import SerializerCategoria
from APPS.Categoria.models import Categoria
from APPS.DetallePedidos.API.SerializerDetallePedido import SerializerDetallePedido
from APPS.DetallePedidos.models import DetallePedido


class DetallePedidoViewsSet (ModelViewSet):

    #permission_classes = [IsAuthenticated]
    queryset = DetallePedido.objects.all()
    serializer_class = SerializerDetallePedido



