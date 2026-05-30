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
            
        # Calcular descuentos de combos promocionales configurados
        from APPS.ComboPedidos.models import ReglaCombo, ComboPedido
        reglas = ReglaCombo.objects.filter(activo=True)
        descuento_combos = Decimal('0.00')
        combos_a_crear = []

        if reglas.exists():
            # Cargar los productos reales para validar de forma segura
            items_productos = []
            for item in items:
                try:
                    item_id = str(item['id'])
                    base_id = int(item_id.split('_custom_')[0]) if '_custom_' in item_id else int(item_id)
                    prod = Producto.objects.get(id=base_id)
                    items_productos.append({
                        'producto': prod,
                        'cantidad': int(item.get('quantity', 1)),
                        'precio': Decimal(str(item.get('price', prod.precio_base)))
                    })
                except (Producto.DoesNotExist, ValueError):
                    continue

            # Copia de cantidades para simular asignaciones de combos y evitar doble conteo
            cantidades_disponibles = { ip['producto'].id: ip['cantidad'] for ip in items_productos }

            for regla in reglas:
                import json
                items_combos = []
                if regla.productos_json:
                    try:
                        items_combos = json.loads(regla.productos_json)
                    except Exception:
                        items_combos = []
                
                if not items_combos:
                    # Fallback para compatibilidad
                    if regla.producto_requerido_id and regla.cantidad_requerida:
                        items_combos.append({
                            'producto_id': regla.producto_requerido_id,
                            'cantidad': regla.cantidad_requerida
                        })
                    if regla.producto_asociado_id and regla.cantidad_asociado:
                        items_combos.append({
                            'producto_id': regla.producto_asociado_id,
                            'cantidad': regla.cantidad_asociado
                        })

                if not items_combos:
                    continue

                # Agrupar requerimientos por ID de producto
                grouped_reqs = {}
                for item in items_combos:
                    pid = int(item.get('producto_id') or item.get('id', 0))
                    qty = int(item.get('cantidad') or item.get('quantity', 0))
                    if pid > 0 and qty > 0:
                        grouped_reqs[pid] = grouped_reqs.get(pid, 0) + qty

                if not grouped_reqs:
                    continue

                # Verificar si todos los productos del combo están presentes y determinar las activaciones posibles
                veces_activado = None
                precios_productos = {}
                for pid, needed in grouped_reqs.items():
                    # Obtener el precio unitario del carrito
                    precio_u = None
                    for ip in items_productos:
                        if ip['producto'].id == pid:
                            precio_u = ip['precio']
                            break
                    if precio_u is None:
                        # Falta este producto en el carrito, no se puede activar
                        veces_activado = 0
                        break
                    precios_productos[pid] = precio_u

                    qty_disponible = cantidades_disponibles.get(pid, 0)
                    posible = qty_disponible // needed
                    if veces_activado is None:
                        veces_activado = posible
                    else:
                        veces_activado = min(veces_activado, posible)

                if veces_activado is not None and veces_activado > 0:
                    # Disminuir cantidades disponibles
                    for pid, needed in grouped_reqs.items():
                        cantidades_disponibles[pid] -= veces_activado * needed

                    # Calcular descuento
                    costo_normal = Decimal('0.00')
                    for pid, needed in grouped_reqs.items():
                        costo_normal += precios_productos[pid] * needed

                    precio_combo_dec = Decimal(str(regla.precio_combo)) if regla.precio_combo else costo_normal
                    descuento_unidad = max(Decimal('0.00'), costo_normal - precio_combo_dec)
                    descuento_total_regla = veces_activado * descuento_unidad

                    if descuento_total_regla > 0:
                        descuento_combos += descuento_total_regla
                        combos_a_crear.append({
                            'nombre': regla.nombre,
                            'descuento_aplicado': descuento_total_regla
                        })

        descuento_total = descuento_combos
        costo_envio = Decimal('0.00')
        total = (subtotal - descuento_total) + costo_envio

        # 1. Crear el Pedido Principal
        pedido = Pedido.objects.create(
            usuario=usuario,
            metodo_entrega=metodo_entrega,
            direccion_exacta=shipping_address if metodo_entrega == 'domicilio' else None,
            subtotal=subtotal,
            descuento_total=descuento_total,
            costo_envio=costo_envio,
            total=total,
            estado='pendiente'
        )

        # Registrar los combos aplicados en la BD
        for cb in combos_a_crear:
            ComboPedido.objects.create(
                pedido=pedido,
                nombre=cb['nombre'],
                descuento_aplicado=cb['descuento_aplicado']
            )

        # 2. Crear los Detalles y descontar Stock
        for item in items:
            item_id = str(item['id'])
            base_id = int(item_id.split('_custom_')[0]) if '_custom_' in item_id else int(item_id)
            producto = Producto.objects.get(id=base_id)
            cantidad = int(item.get('quantity', 1))
            price = Decimal(str(item.get('price', producto.precio_base)))
            
            # Reducir stock (Opcional, según lo que me confirmen, pero lo dejamos como valor por defecto seguro)
            if producto.stock >= cantidad:
                producto.stock -= cantidad
                producto.save()
                
            import json
            custom_data = {
                "description": item.get('description'),
                "wood_hex": item.get('wood_hex'),
                "fabric_hex": item.get('fabric_hex')
            }
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio=price,
                detalles_personalizacion=json.dumps(custom_data) if (item.get('description') or item.get('wood_hex') or item.get('fabric_hex')) else None
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
        data['shipping_address'] = instance.direccion_exacta
        data['created_at'] = instance.creado_en.strftime("%Y-%m-%dT%H:%M:%SZ") if instance.creado_en else None
        
        estado_map = {
            'pendiente': 'pending',
            'en_proceso': 'processing',
            'listo': 'ready',
            'entregado': 'delivered',
            'cancelado': 'cancelled',
            'devolucion_pendiente': 'refund_pending',
            'devuelto': 'refunded',
            'pending': 'pending',
            'payment_review': 'payment_review',
            'payment_validated': 'payment_validated',
            'processing': 'processing',
            'ready': 'ready',
            'delivered': 'delivered',
            'cancelled': 'cancelled',
            'refund_pending': 'refund_pending',
            'refunded': 'refunded',
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
        
        # Datos de Pago del Mueble
        pago_productos = instance.pagos.filter(tipo_pago='productos').first()
        if pago_productos:
            data['payment_method'] = 'paypal' if pago_productos.metodo_pago == 'paypal' else 'receipt'
            data['paypal_order_id'] = pago_productos.id_transaccion
            data['payment_receipt_url'] = pago_productos.imagen_comprobante.url if pago_productos.imagen_comprobante else None
        else:
            data['payment_method'] = 'receipt'
            data['paypal_order_id'] = None
            data['payment_receipt_url'] = None

        # Shipping status y datos de pago de delivery
        pago_delivery = instance.pagos.filter(tipo_pago='delivery').first()
        if pago_delivery:
            # Si el pago está completado, el estado es 'validated' (validado por admin)
            # Si está pendiente, el estado es 'paid' (pagado por cliente, pendiente de revisar)
            data['shipping_status'] = 'validated' if pago_delivery.estado == 'completado' else 'paid'
            data['shipping_payment_method'] = 'paypal' if pago_delivery.metodo_pago == 'paypal' else 'receipt'
            data['shipping_paypal_order_id'] = pago_delivery.id_transaccion
            data['shipping_payment_receipt_url'] = pago_delivery.imagen_comprobante.url if pago_delivery.imagen_comprobante else None
        else:
            # Si no hay pago pero se cotizó, el estado es 'quoted'
            if instance.costo_envio > 0:
                data['shipping_status'] = 'quoted'
            else:
                data['shipping_status'] = 'pending'
            
        return data
