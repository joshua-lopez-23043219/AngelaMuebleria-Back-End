from rest_framework.routers import DefaultRouter

from APPS.Facturas.API.FacturaAPI import FacturaViewsSet

routerFactura = DefaultRouter()

routerFactura.register(r'Factura', FacturaViewsSet ,basename='Factura')