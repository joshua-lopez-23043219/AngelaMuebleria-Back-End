from rest_framework import serializers
from APPS.Personalizacion.models import MuebleBase, ColorMaterial

class SerializerMuebleBase(serializers.ModelSerializer):
    class Meta:
        model = MuebleBase
        fields = '__all__'

class SerializerColorMaterial(serializers.ModelSerializer):
    class Meta:
        model = ColorMaterial
        fields = '__all__'
