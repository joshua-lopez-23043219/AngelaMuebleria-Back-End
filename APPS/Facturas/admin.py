from django.contrib import admin

from APPS.Facturas.models import Factura


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['pedido','numero_factura','subtotal','impuesto','total','url_pdf']
    search_fields = ['pedido','numero_factura','subtotal','impuesto','total','url_pdf']
# Register your models here.
