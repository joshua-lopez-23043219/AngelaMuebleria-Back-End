from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.Municipio.API.SerializerMunicipio import SerializerMunicipio
from APPS.Municipio.models import Municipio


class MunicipioViewsSet (ModelViewSet):

    permission_classes = [IsAuthenticated]
    queryset = Municipio.objects.all()
    serializer_class = SerializerMunicipio



