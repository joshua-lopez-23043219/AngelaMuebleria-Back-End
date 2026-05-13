from django.contrib import admin

from APPS.ComboPedidos.models import ComboPedido


@admin.register(ComboPedido)
class ComboPedidoAdmin(admin.ModelAdmin):
    list_display = ['pedido','nombre','descuento_aplicado','creado_en']
    search_fields = ['pedido','nombre','descuento_aplicado','creado_en']
# Register your models here.
