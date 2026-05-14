from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.Departamento.API.SerializerDepartamento import SerializerDepartamento
from APPS.Departamento.models import Departamento


class DepartamentoViewsSet (ModelViewSet):

    #permission_classes = [IsAuthenticated]
    queryset = Departamento.objects.all()
    serializer_class = SerializerDepartamento




