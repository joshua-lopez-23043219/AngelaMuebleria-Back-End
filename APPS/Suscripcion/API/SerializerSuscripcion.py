from rest_framework import serializers
from APPS.Suscripcion.models import Suscriptor

class SerializerSuscriptor(serializers.ModelSerializer):
    class Meta:
        model = Suscriptor
        fields = ['id', 'email', 'codigo_descuento', 'porcentaje_descuento', 'fue_usado', 'creado_en']
        read_only_fields = ['codigo_descuento', 'porcentaje_descuento', 'fue_usado', 'creado_en']
