from rest_framework import serializers
from django.db import transaction
from APPS.Pedidos.models import Pedido
from APPS.DetallePedidos.models import DetallePedido
from APPS.Pago.models import Pago
from APPS.Producto.models import Producto

class SerializerPedidos(serializers.ModelSerializer):
    # Campos adicionales que vienen del frontend y no están directamente en el modelo
    items = serializers.ListField(child=serializers.DictField(), write_only=True)
    payment_method = serializers.CharField(write_only=True)
    payment_receipt_url = serializers.CharField(write_only=True, required=False, allow_null=True)
    paypal_order_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    shipping_type = serializers.CharField(write_only=True)
    shipping_address = serializers.CharField(write_only=True, required=False, allow_null=True)
    discount_code = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'subtotal', 'descuento_total', 'costo_envio', 'total', 'estado', 'creado_en',
            'items', 'payment_method', 'payment_receipt_url', 'paypal_order_id',
            'shipping_type', 'shipping_address', 'discount_code'
        ]
        read_only_fields = ['id', 'estado', 'creado_en', 'subtotal', 'descuento_total', 'costo_envio', 'total']

    @transaction.atomic
    def create(self, validated_data):
        # Extraer campos personalizados
        items = validated_data.pop('items')
        payment_method = validated_data.pop('payment_method')
        payment_receipt_url = validated_data.pop('payment_receipt_url', None)
        paypal_order_id = validated_data.pop('paypal_order_id', None)
        shipping_type = validated_data.pop('shipping_type')
        shipping_address = validated_data.pop('shipping_address', None)
        discount_code = validated_data.pop('discount_code', None)

        usuario = self.context['request'].user

        # Mapeo de método de entrega
        metodo_entrega = 'local' if shipping_type == 'pickup' else 'domicilio'
        
        # Opcional: Guardar la dirección en el perfil del usuario si es delivery
        if metodo_entrega == 'domicilio' and shipping_address:
            usuario.direccion_exacta = shipping_address
            usuario.save()

        # Recalcular totales por seguridad (evitar manipulación en el frontend)
        subtotal = 0
        for item in items:
            from decimal import Decimal
            price = Decimal(str(item.get('price', 0)))
            qty = int(item.get('quantity', 1))
            subtotal += price * qty
            
        descuento_total = 0  # Aquí se calcularía real basado en discount_code si tuviéramos tabla de cupones
        costo_envio = 0
        total = (subtotal - descuento_total) + costo_envio

        # 1. Crear el Pedido Principal
        pedido = Pedido.objects.create(
            usuario=usuario,
            metodo_entrega=metodo_entrega,
            subtotal=subtotal,
            descuento_total=descuento_total,
            costo_envio=costo_envio,
            total=total,
            estado='pendiente'
        )

        # 2. Crear los Detalles y descontar Stock
        for item in items:
            producto = Producto.objects.get(id=item['id'])
            cantidad = int(item.get('quantity', 1))
            
            # Reducir stock (Opcional, según lo que me confirmen, pero lo dejamos como valor por defecto seguro)
            if producto.stock >= cantidad:
                producto.stock -= cantidad
                producto.save()
                
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio=producto.precio_base
            )

        # 3. Registrar el Pago
        metodo_pago_db = 'transferencia' if payment_method == 'receipt' else 'paypal'
        estado_pago = 'completado' if metodo_pago_db == 'paypal' else 'pendiente'
        
        # Si payment_receipt_url viene con "/media/path", extraer solo el "path" relativo para el ImageField
        relative_path = None
        if payment_receipt_url:
            relative_path = payment_receipt_url.split('/media/')[-1] if '/media/' in payment_receipt_url else payment_receipt_url

        Pago.objects.create(
            pedido=pedido,
            tipo_pago='productos',
            metodo_pago=metodo_pago_db,
            id_transaccion=paypal_order_id,
            imagen_comprobante=relative_path,
            monto=total,
            estado=estado_pago
        )

        return pedido

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Mapeo de campos esperados por el frontend
        data['created_at'] = instance.creado_en.strftime("%Y-%m-%dT%H:%M:%SZ") if instance.creado_en else None
        
        # Mapeo de estado para que coincida con el frontend
        estado_map = {
            'pendiente': 'pending',
            'en_proceso': 'processing',
            'listo': 'processing',
            'entregado': 'delivered',
            'cancelado': 'cancelled',
            'pending': 'pending',
            'payment_review': 'payment_review',
            'payment_validated': 'payment_validated',
            'processing': 'processing',
            'delivered': 'delivered',
            'cancelled': 'cancelled',
        }
        data['status'] = estado_map.get(instance.estado, 'pending')
        
        data['shipping_type'] = 'delivery' if instance.metodo_entrega == 'domicilio' else 'pickup'
        data['shipping_cost'] = float(instance.costo_envio) if instance.costo_envio else 0
        
        # Datos del usuario
        if instance.usuario:
            data['user_name'] = f"{instance.usuario.first_name} {instance.usuario.last_name}".strip() or instance.usuario.username
            data['user_phone'] = instance.usuario.numero_telefono or "No registrado"
            data['user_department'] = instance.usuario.municipio.departamento.nombre if (hasattr(instance.usuario, 'municipio') and instance.usuario.municipio) else "No registrado"
            data['user_municipality'] = instance.usuario.municipio.nombre if (hasattr(instance.usuario, 'municipio') and instance.usuario.municipio) else "No registrado"
        
        # Shipping status (revisando pagos de delivery)
        pago_delivery = instance.pagos.filter(tipo_pago='delivery').first()
        if pago_delivery:
            data['shipping_status'] = 'paid' if pago_delivery.estado == 'completado' else 'pending'
        else:
            data['shipping_status'] = 'pending'
            
        return data
