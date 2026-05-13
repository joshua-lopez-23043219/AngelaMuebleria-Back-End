from django.db import connection
from rest_framework.serializers import ModelSerializer

from APPS.Categoria.models import Categoria


class SerializerCategoria (ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
