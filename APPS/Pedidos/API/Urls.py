from rest_framework.routers import DefaultRouter

from APPS.Pedidos.API.PedidosAPI import PedidosViewsSet

routerPedidos = DefaultRouter()

routerPedidos.register(r'Pedidos', PedidosViewsSet ,basename='Pedidos')