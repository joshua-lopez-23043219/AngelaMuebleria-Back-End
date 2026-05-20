from django.db import connection
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from APPS.ComboPedidos.models import ComboPedido, ReglaCombo


class SerializerComboPedido (ModelSerializer):
    class Meta:
        model = ComboPedido
        fields ='__all__'


class SerializerReglaCombo(ModelSerializer):
    categoria_requerida_nombre = serializers.ReadOnlyField(source='categoria_requerida.nombre')
    categoria_regalo_nombre = serializers.ReadOnlyField(source='categoria_regalo.nombre')

    class Meta:
        model = ReglaCombo
        fields = '__all__'


