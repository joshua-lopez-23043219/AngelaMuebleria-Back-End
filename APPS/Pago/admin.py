from django.contrib import admin

from APPS.Pago.models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['pedido','tipo_pago','metodo_pago','id_transaccion','imagen_comprobante','monto','estado','creado_en','verificado_en']
    search_fields = ['pedido','tipo_pago','metodo_pago','id_transaccion','imagen_comprobante','monto','estado','creado_en','verificado_en']
# Register your models here.
