from rest_framework.routers import DefaultRouter

from APPS.Suscripcion.API.SuscripcionAPI import SuscripcionViewsSet

routerSuscripcion = DefaultRouter()

routerSuscripcion.register(r'Suscripcion', SuscripcionViewsSet ,basename='Suscripcion')
