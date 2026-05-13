from rest_framework.routers import DefaultRouter

from APPS.DetallePedidos.API.DetallePedidoAPI import DetallePedidoViewsSet

routerDetallePedido = DefaultRouter()

routerDetallePedido.register(r'DetallePedido', DetallePedidoViewsSet ,basename='DetallePedido')