from django.db import connection
from rest_framework.serializers import ModelSerializer


from APPS.Producto.models import Producto


class SerializerProducto (ModelSerializer):
    class Meta:
        model = Producto
        fields ='__all__'

