from django.contrib import admin

from Seguridad.Usuarios.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['rol','numero_telefono','municipio','direccion_exacta','email_verificado']
    search_fields = ['rol','numero_telefono','municipio','direccion_exacta','email_verificado']
# Register your models here.
