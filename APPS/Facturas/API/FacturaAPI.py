from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from APPS.Facturas.API.SerializerFactura import SerializerFactura
from APPS.Facturas.models import Factura


class FacturaViewsSet (ModelViewSet):

    #permission_classes = [IsAuthenticated]
    queryset = Factura.objects.all()
    serializer_class = SerializerFactura



