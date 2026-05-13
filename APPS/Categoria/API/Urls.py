from rest_framework.routers import DefaultRouter

from APPS.Categoria.API.CategoriaAPI import CategoriaViewsSet

routerCategoria = DefaultRouter()

routerCategoria.register(r'Categoria', CategoriaViewsSet ,basename='Categoria')