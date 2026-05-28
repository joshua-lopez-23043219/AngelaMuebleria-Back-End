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
        user = self.request.user
        is_admin = user.is_superuser or (hasattr(user, 'rol') and user.rol == 'admin')
        if is_admin:
            return Pedido.objects.all().order_by('-creado_en')
        return Pedido.objects.filter(usuario=user).order_by('-creado_en')

    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        is_admin = user.is_superuser or (hasattr(user, 'rol') and user.rol == 'admin')
        if not is_admin:
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
            
        from APPS.Producto.models import Producto
        
        # Ingresos Totales (Solo de productos por ahora)
        from django.db.models import Sum
        revenue = Pedido.objects.filter(estado__in=['en_proceso', 'listo', 'entregado']).aggregate(total=Sum('total'))['total'] or 0
        
        # Devoluciones (Devuelto)
        refunded_amount = Pedido.objects.filter(estado='devuelto').aggregate(total=Sum('total'))['total'] or 0
        refunded_orders = Pedido.objects.filter(estado='devuelto').count()
        
        # Devoluciones por fecha (Semanal y mensual)
        from django.utils import timezone
        import datetime
        now = timezone.now()
        start_of_week = now - datetime.timedelta(days=7)
        start_of_month = now - datetime.timedelta(days=30)
        
        refunded_this_week = Pedido.objects.filter(estado='devuelto', actualizado_en__gte=start_of_week).aggregate(total=Sum('total'))['total'] or 0
        refunded_this_month = Pedido.objects.filter(estado='devuelto', actualizado_en__gte=start_of_month).aggregate(total=Sum('total'))['total'] or 0
        
        data = {
            "revenue": float(revenue),
            "orders": Pedido.objects.exclude(estado='cancelado').count(),
            "products": Producto.objects.count(),
            "lowStock": Producto.objects.filter(stock__lt=5).count(),
            "refundedAmount": float(refunded_amount),
            "refundedOrders": refunded_orders,
            "refundedThisWeek": float(refunded_this_week),
            "refundedThisMonth": float(refunded_this_month)
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def mis_pedidos(self, request):
        pedidos = self.queryset.filter(usuario=request.user)
        serializer = self.get_serializer(pedidos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
            'cancelled': 'cancelado',
            'refund_pending': 'devolucion_pendiente',
            'refunded': 'devuelto'
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
                
        # Lógica extra: Si se aprueba/efectúa la devolución (estado es devuelto)
        if estado_db == 'devuelto':
            from django.db import transaction
            with transaction.atomic():
                # Reembolsar pagos si aplica
                for pago in pedido.pagos.all():
                    if pago.estado in ['completado', 'pendiente']:
                        pago.estado = 'reembolsado'
                        pago.save()
                
                # Devolver stock a los productos
                for detalle in pedido.detalles.all():
                    producto = detalle.producto
                    producto.stock += detalle.cantidad
                    producto.save()
        
        # Devolver el objeto serializado actualizado
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancelar(self, request, pk=None):
        pedido = self.get_object()
        
        # Verificar permisos: El pedido pertenece al usuario o es administrador
        is_admin = request.user.is_superuser or (hasattr(request.user, 'rol') and request.user.rol == 'admin')
        if pedido.usuario != request.user and not is_admin:
            return Response({"error": "No tienes permiso para cancelar este pedido"}, status=status.HTTP_403_FORBIDDEN)
            
        if pedido.estado == 'cancelado':
            return Response({"error": "El pedido ya se encuentra cancelado"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Si ya fue entregado, no se permite la cancelación
        if pedido.estado == 'entregado':
            return Response({"error": "No se puede cancelar un pedido entregado"}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.db import transaction
        with transaction.atomic():
            pedido.estado = 'cancelado'
            pedido.save()
            
            # Devolver stock a los productos
            for detalle in pedido.detalles.all():
                producto = detalle.producto
                producto.stock += detalle.cantidad
                producto.save()
                
            # Reembolsar pagos si aplica
            for pago in pedido.pagos.all():
                if pago.estado == 'completado' or pago.estado == 'pendiente':
                    pago.estado = 'reembolsado'
                    pago.save()
                    
        serializer = self.get_serializer(pedido)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def solicitar_devolucion(self, request, pk=None):
        pedido = self.get_object()
        
        # Verificar permisos: El pedido pertenece al usuario o es administrador
        is_admin = request.user.is_superuser or (hasattr(request.user, 'rol') and request.user.rol == 'admin')
        if pedido.usuario != request.user and not is_admin:
            return Response({"error": "No tienes permiso para solicitar devolución de este pedido"}, status=status.HTTP_403_FORBIDDEN)
            
        if pedido.estado in ['cancelado', 'devolucion_pendiente', 'devuelto']:
            return Response({"error": f"El pedido no se encuentra en un estado elegible para devolución. Estado actual: {pedido.estado}"}, status=status.HTTP_400_BAD_REQUEST)
            
        pedido.estado = 'devolucion_pendiente'
        pedido.save()
        
        serializer = self.get_serializer(pedido)
        return Response(serializer.data, status=status.HTTP_200_OK)
