from django.contrib import admin

from APPS.Suscripcion.models import Suscriptor


@admin.register(Suscriptor)
class SuscriptorAdmin(admin.ModelAdmin):
    list_display = ['email', 'codigo_descuento', 'porcentaje_descuento', 'fue_usado', 'creado_en']
    search_fields = ['email', 'codigo_descuento']
    list_filter = ['fue_usado']
# Register your models here.
