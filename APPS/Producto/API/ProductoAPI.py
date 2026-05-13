from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.Producto.API.SerializerProducto import SerializerProducto
from APPS.Producto.models import Producto


class ProductoViewsSet (ModelViewSet):

    #permission_classes = [IsAuthenticated]
    queryset = Producto.objects.all()
    serializer_class = SerializerProducto



