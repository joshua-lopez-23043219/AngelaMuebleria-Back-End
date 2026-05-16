from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.Pedidos.API.SerializerPedidos import SerializerPedidos
from APPS.Pedidos.models import Pedido


class PedidosViewsSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Pedido.objects.all().order_by('-creado_en')
    serializer_class = SerializerPedidos

    def get_queryset(self):
        # Si es admin, ve todos. Si es cliente, solo los suyos.
        if hasattr(self.request.user, 'rol') and self.request.user.rol == 'admin':
            return self.queryset
        return self.queryset.filter(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def mis_pedidos(self, request):
        pedidos = self.queryset.filter(usuario=request.user)
        # Necesitamos devolver un json amigable para el frontend
        data = []
        for p in pedidos:
            data.append({
                "id": p.id,
                "total": p.total,
                "status": {
                    'pendiente': 'pending', 
                    'en_proceso': 'processing', 
                    'listo': 'ready', 
                    'entregado': 'delivered', 
                    'cancelado': 'cancelled'
                }.get(p.estado, p.estado),

                "created_at": p.creado_en.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "shipping_type": p.metodo_entrega,
            })
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def get_detalles(self, request, pk=None):
        pedido = self.get_object()
        detalles = pedido.detalles.all()
        data = []
        for d in detalles:
            data.append({
                "id": d.producto.id,
                "name": d.producto.nombre,
                "price": d.precio,
                "quantity": d.cantidad,
                "image_url": d.producto.url_miniatura.url if d.producto.url_miniatura else None
            })
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        if not (hasattr(request.user, 'rol') and request.user.rol == 'admin'):
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
            
        pedido = self.get_object()
        nuevo_estado = request.data.get('status')
        
        if not nuevo_estado:
            return Response({"error": "Estado no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)

        # Mapeo de estados del frontend a estados del modelo (Español)
        reverse_map = {
            'pending': 'pendiente',
            'payment_review': 'payment_review',
            'payment_validated': 'payment_validated',
            'processing': 'en_proceso',
            'ready': 'listo',
            'delivered': 'entregado',
            'cancelled': 'cancelado'
        }
        
        estado_db = reverse_map.get(nuevo_estado, nuevo_estado)
        pedido.estado = estado_db
        pedido.save()
        
        # Lógica extra: Si se valida el pago, actualizar el registro de Pago a 'completado'
        if nuevo_estado == 'payment_validated':
            pago = pedido.pagos.filter(tipo_pago='productos').first()
            if pago:
                pago.estado = 'completado'
                pago.save()
        
        return Response({
            "message": "Estado actualizado", 
            "new_status": nuevo_estado,
            "db_status": estado_db
        })
