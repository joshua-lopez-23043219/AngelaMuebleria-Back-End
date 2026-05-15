"""
URL configuration for Config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView

from APPS.Categoria.API.Urls import routerCategoria
from APPS.ComboPedidos.API.Urls import routerComboPedido
from APPS.Departamento.API.Urls import routerDepartamento
from APPS.DetallePedidos.API.Urls import routerDetallePedido
from APPS.Facturas.API.Urls import routerFactura
from APPS.Municipio.API.Urls import routerMunicipio
from APPS.Pago.API.Urls import routerPago
from APPS.Pedidos.API.Urls import routerPedidos
from APPS.Producto.API.Urls import routerProducto
from APPS.Suscripcion.API.Urls import routerSuscripcion
from APPS.VarianteProducto.API.Urls import routerVarianteProducto
from Config import settings
from Config.views import upload_file
from Seguridad.Usuarios.API.Urls import routerUsuario
from Seguridad.Usuarios.API.AuthSerializer import MyTokenObtainPairSerializer

class MyTokenObtainPairView (TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('apiCategoria/', include(routerCategoria.urls)),
    path('apiComboPedido/', include(routerComboPedido.urls)),
    path('apiDepartamento/', include(routerDepartamento.urls)),
    path('apiDetallePedido/', include(routerDetallePedido.urls)),
    path('apiFactura/',include(routerFactura.urls)),
    path('apiMunicipio/', include(routerMunicipio.urls)),
    path('apiPago/', include(routerPago.urls)),
    path('apiPedidos/', include(routerPedidos.urls)),
    path('apiProducto/', include(routerProducto.urls)),
    path('apiSuscripcion/', include(routerSuscripcion.urls)),
    path('apiVarianteProducto/',include(routerVarianteProducto.urls)),
    path('apiUsuarios/',include(routerUsuario.urls)),

    # Endpoint de subida genérica para comprobantes
    path('api/upload/', upload_file, name='upload_file'),

    # Ruta para obtener el token (Login)
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Ruta para renovar el token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Servir archivos media
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG or os.environ.get('RAILWAY_ENVIRONMENT'):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
