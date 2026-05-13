from django.db import connection
from rest_framework.serializers import ModelSerializer

from APPS.Categoria.models import Categoria
from APPS.DetallePedidos.models import DetallePedido


class SerializerDetallePedido (ModelSerializer):
    class Meta:
        model = DetallePedido
        fields ='__all__'

