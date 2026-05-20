from rest_framework.routers import DefaultRouter

from APPS.ComboPedidos.API.ComboPedidoAPI import ComboPedidoViewsSet, ReglaComboViewsSet

routerComboPedido = DefaultRouter()

routerComboPedido.register(r'ComboPedido', ComboPedidoViewsSet ,basename='ComboPedido')
routerComboPedido.register(r'ReglaCombo', ReglaComboViewsSet ,basename='ReglaCombo')