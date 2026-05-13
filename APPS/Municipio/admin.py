from django.contrib import admin

from APPS.Municipio.models import Municipio


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['nombre','departamento']
    search_fields = ['nombre','departamento']
# Register your models here.
