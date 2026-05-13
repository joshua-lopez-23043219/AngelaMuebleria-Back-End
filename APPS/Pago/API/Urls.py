from rest_framework.routers import DefaultRouter

from APPS.Pago.API.PagoAPI import PagoViewsSet

routerPago = DefaultRouter()

routerPago.register(r'Pago', PagoViewsSet ,basename='Pago')