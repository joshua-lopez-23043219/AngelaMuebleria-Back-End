from django.contrib import admin

from APPS.Departamento.models import Departamento


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields =['nombre']
# Register your models here.
