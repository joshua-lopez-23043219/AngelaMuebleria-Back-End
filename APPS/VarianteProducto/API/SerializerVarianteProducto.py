from django.db import connection
from rest_framework.serializers import ModelSerializer

from APPS.Categoria.models import Categoria
from APPS.VarianteProducto.models import VarianteProducto


class SerializerVarianteProducto (ModelSerializer):
    class Meta:
        model = VarianteProducto
        fields ='__all__'

