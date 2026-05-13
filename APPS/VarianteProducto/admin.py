from django.contrib import admin

from APPS.VarianteProducto.models import VarianteProducto


@admin.register(VarianteProducto)
class VarianteProductoAdmin(admin.ModelAdmin):
    list_display = ['producto','nombre_color','hex_color','ajuste_precio']
    search_fields = ['producto','nombre_color','hex_color','ajuste_precio']
# Register your models here.
