from rest_framework.routers import DefaultRouter

from APPS.VarianteProducto.API.VarianteProductoAPI import VarianteProductoViewsSet

routerVarianteProducto = DefaultRouter()

routerVarianteProducto.register(r'VarianteProducto', VarianteProductoViewsSet ,basename='VarianteProducto')