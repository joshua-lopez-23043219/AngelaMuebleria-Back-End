from rest_framework.routers import DefaultRouter

from APPS.ComboPedidos.API.ComboPedidoAPI import ComboPedidoViewsSet

routerComboPedido = DefaultRouter()

routerComboPedido.register(r'ComboPedido', ComboPedidoViewsSet ,basename='ComboPedido')