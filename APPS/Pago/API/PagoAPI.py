from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.Pago.API.SerializerPago import SerializerPago
from APPS.Pago.models import Pago

class PagoViewsSet (ModelViewSet):

    #permission_classes = [IsAuthenticated]
    queryset = Pago.objects.all()
    serializer_class = SerializerPago



