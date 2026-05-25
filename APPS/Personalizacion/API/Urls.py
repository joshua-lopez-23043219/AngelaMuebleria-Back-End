from rest_framework.routers import DefaultRouter
from APPS.Personalizacion.API.PersonalizacionAPI import MuebleBaseViewsSet, ColorMaterialViewsSet

routerPersonalizacion = DefaultRouter()
routerPersonalizacion.register(r'MuebleBase', MuebleBaseViewsSet, basename='MuebleBase')
routerPersonalizacion.register(r'ColorMaterial', ColorMaterialViewsSet, basename='ColorMaterial')
