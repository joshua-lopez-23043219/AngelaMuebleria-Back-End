from django.db import connection
from rest_framework.serializers import ModelSerializer

from APPS.Categoria.models import Categoria
from APPS.Facturas.models import Factura


class SerializerFactura (ModelSerializer):
    class Meta:
        model = Factura
        fields ='__all__'

