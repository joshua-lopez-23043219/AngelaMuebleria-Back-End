from django.contrib import admin

from APPS.DetallePedidos.models import DetallePedido


@admin.register(DetallePedido)
class DetallePedidosAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'combo','producto','variante','cantidad','precio','es_regalo']
    search_fields = ['pedido', 'combo','producto','variante','cantidad','precio','es_regalo']
# Register your models here.
