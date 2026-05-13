from django.db import connection
from rest_framework.serializers import ModelSerializer

from APPS.Municipio.models import Municipio


class SerializerMunicipio (ModelSerializer):
    class Meta:
        model = Municipio
        fields ='__all__'

