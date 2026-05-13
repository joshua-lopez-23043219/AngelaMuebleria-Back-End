from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.VarianteProducto.API.SerializerVarianteProducto import SerializerVarianteProducto
from APPS.VarianteProducto.models import VarianteProducto


class VarianteProductoViewsSet (ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = VarianteProducto.objects.all()
    serializer_class = SerializerVarianteProducto



