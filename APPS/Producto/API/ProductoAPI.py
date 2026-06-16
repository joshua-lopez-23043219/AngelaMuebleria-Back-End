from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.Producto.API.SerializerProducto import SerializerProducto
from APPS.Producto.models import Producto


class ProductoViewsSet (ModelViewSet):

    #permission_classes = [IsAuthenticated]
    queryset = Producto.objects.all()
    serializer_class = SerializerProducto

    @action(detail=False, methods=['get'], url_path='landbot', permission_classes=[AllowAny])
    def landbot(self, request):
        productos = Producto.objects.filter(esta_activo=True)
        response_data = []
        for p in productos:
            if p.url_miniatura:
                imagen_url = request.build_absolute_uri(p.url_miniatura.url)
            else:
                imagen_url = f"https://picsum.photos/seed/{p.nombre}/500/500"
                
            try:
                precio_val = float(p.precio_base)
                if precio_val.is_integer():
                    precio_str = f"C$ {int(precio_val):,}"
                else:
                    precio_str = f"C$ {precio_val:,.2f}"
            except (ValueError, TypeError):
                precio_str = f"C$ {p.precio_base}"

            response_data.append({
                "id": p.id,
                "nombre": p.nombre,
                "precio": precio_str,
                "imagen_url": imagen_url
            })
        return Response(response_data, status=status.HTTP_200_OK)
