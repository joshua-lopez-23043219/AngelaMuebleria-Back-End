from rest_framework.routers import DefaultRouter
from APPS.Personalizacion.API.PersonalizacionAPI import (
    MuebleBaseViewsSet, ColorMaterialViewsSet, MuebleColorModelo3DViewsSet
)

routerPersonalizacion = DefaultRouter()
routerPersonalizacion.register(r'MuebleBase', MuebleBaseViewsSet, basename='MuebleBase')
routerPersonalizacion.register(r'ColorMaterial', ColorMaterialViewsSet, basename='ColorMaterial')
routerPersonalizacion.register(r'MuebleColorModelo3D', MuebleColorModelo3DViewsSet, basename='MuebleColorModelo3D')
