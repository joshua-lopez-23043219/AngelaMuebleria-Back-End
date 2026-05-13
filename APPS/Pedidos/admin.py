from django.contrib import admin

from APPS.Pedidos.models import Pedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['usuario','metodo_entrega','subtotal','descuento_total','costo_envio','total','estado','creado_en','actualizado_en']
    search_fields = ['usuario','metodo_entrega','subtotal','descuento_total','costo_envio','total','estado','creado_en','actualizado_en']
# Register your models here.
