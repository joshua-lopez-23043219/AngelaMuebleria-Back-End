from django.db import connection
from rest_framework.serializers import ModelSerializer


from APPS.Departamento.models import Departamento


class SerializerDepartamento (ModelSerializer):
    class Meta:
        model = Departamento
        fields ='__all__'

