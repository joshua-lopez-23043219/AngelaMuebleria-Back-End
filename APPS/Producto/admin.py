from django.contrib import admin

from APPS.Producto.models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre','codigo_producto','tipo_producto','categoria','precio_base','stock','esta_activo','descripcion','materiales','dimensiones','url_miniatura','url_modelo_3d']
    search_fields = ['nombre','codigo_producto','tipo_producto','categoria','precio_base','stock','esta_activo','descripcion','materiales','dimensiones','url_miniatura','url_modelo_3d']
# Register your models here.
