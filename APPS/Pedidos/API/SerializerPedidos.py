from django.db import connection
from rest_framework.serializers import ModelSerializer

from APPS.Pedidos.models import Pedido


class SerializerPedidos (ModelSerializer):
    class Meta:
        model = Pedido
        fields ='__all__'

