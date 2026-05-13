from django.db import connection
from rest_framework.serializers import ModelSerializer

from APPS.ComboPedidos.models import ComboPedido


class SerializerComboPedido (ModelSerializer):
    class Meta:
        model = ComboPedido
        fields ='__all__'

