from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from APPS.ComboPedidos.models import ComboPedido, ReglaCombo


class SerializerComboPedido (ModelSerializer):
    class Meta:
        model = ComboPedido
        fields ='__all__'


class SerializerReglaCombo(ModelSerializer):
    producto_requerido_nombre = serializers.SerializerMethodField()
    producto_asociado_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ReglaCombo
        fields = '__all__'

    def get_producto_requerido_nombre(self, obj):
        if obj.producto_requerido:
            return obj.producto_requerido.nombre
        return "Producto no asignado"

    def get_producto_asociado_nombre(self, obj):
        if obj.producto_asociado:
            return obj.producto_asociado.nombre
        return "Producto no asignado"

