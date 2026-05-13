from django.db import connection
from rest_framework.serializers import ModelSerializer


from APPS.Pago.models import Pago

class SerializerPago (ModelSerializer):
    class Meta:
        model = Pago
        fields ='__all__'

