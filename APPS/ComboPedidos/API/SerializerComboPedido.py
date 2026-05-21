from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from APPS.ComboPedidos.models import ComboPedido, ReglaCombo


class SerializerComboPedido (ModelSerializer):
    class Meta:
        model = ComboPedido
        fields ='__all__'


class SerializerReglaCombo(ModelSerializer):
    producto_requerido_nombre = serializers.ReadOnlyField(source='producto_requerido.nombre')
    producto_asociado_nombre = serializers.ReadOnlyField(source='producto_asociado.nombre')

    class Meta:
        model = ReglaCombo
        fields = '__all__'
