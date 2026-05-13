from rest_framework.routers import DefaultRouter

from APPS.Municipio.API.MunicipioAPI import MunicipioViewsSet

routerMunicipio = DefaultRouter()

routerMunicipio.register(r'Municipio', MunicipioViewsSet ,basename='Municipio')