from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.Categoria.API.SerializerCategoria import SerializerCategoria
from APPS.Categoria.models import Categoria


class CategoriaViewsSet (ModelViewSet):

    #permission_classes = [IsAuthenticated]
    queryset = Categoria.objects.all()
    serializer_class = SerializerCategoria



