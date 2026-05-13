from rest_framework.routers import DefaultRouter

from APPS.Producto.API.ProductoAPI import ProductoViewsSet

routerProducto = DefaultRouter()

routerProducto.register(r'Producto', ProductoViewsSet ,basename='Producto')