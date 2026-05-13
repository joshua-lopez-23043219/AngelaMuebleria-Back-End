from rest_framework.routers import DefaultRouter

from APPS.Departamento.API.DepartamentoAPI import DepartamentoViewsSet

routerDepartamento = DefaultRouter()

routerDepartamento.register(r'Departamento', DepartamentoViewsSet ,basename='Departamento')