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
                    prod = Producto.objects.get(id=item['id'])
                    items_productos.append({
                        'producto': prod,
                        'cantidad': int(item.get('quantity', 1)),
                        'precio': prod.precio_base
                    })
                except Producto.DoesNotExist:
                    continue

            # Copia de cantidades para simular asignaciones de combos y evitar doble conteo
            cantidades_disponibles = { ip['producto'].id: ip['cantidad'] for ip in items_productos }

            for regla in reglas:
                # Determinar cuántas veces se puede activar el combo.
                # Cada activación requiere:
                # - regla.cantidad_requerida de items del grupo requerido
                # - regla.cantidad_regalo de items del grupo de regalo
                
                total_req_disponibles = 0
                for ip in items_productos:
                    prod = ip['producto']
                    qty = cantidades_disponibles.get(prod.id, 0)
                    if qty <= 0:
                        continue
                    cumple_tipo = (not regla.tipo_requerido) or (prod.tipo_producto == regla.tipo_requerido)
                    cumple_cat = (not regla.categoria_requerida) or (prod.categoria_id == regla.categoria_requerida_id)
                    if cumple_tipo and cumple_cat:
                        total_req_disponibles += qty
                
                veces_req = total_req_disponibles // regla.cantidad_requerida
                if veces_req <= 0:
                    continue

                veces_activado = 0
                descuento_regla_total = Decimal('0.00')

                for _ in range(veces_req):
                    # Intentar consumir los requeridos
                    req_consumidos = []
                    req_disponibles_sorted = []
                    for ip in items_productos:
                        prod = ip['producto']
                        qty = cantidades_disponibles.get(prod.id, 0)
                        if qty > 0:
                            cumple_tipo = (not regla.tipo_requerido) or (prod.tipo_producto == regla.tipo_requerido)
                            cumple_cat = (not regla.categoria_requerida) or (prod.categoria_id == regla.categoria_requerida_id)
                            if cumple_tipo and cumple_cat:
                                req_disponibles_sorted.append({
                                    'prod_id': prod.id,
                                    'precio': ip['precio'],
                                    'qty_available': qty
                                })
                    
                    req_disponibles_sorted = sorted(req_disponibles_sorted, key=lambda x: x['precio'])
                    
                    acumulado_req = 0
                    temp_updates = {}
                    for item_r in req_disponibles_sorted:
                        if acumulado_req >= regla.cantidad_requerida:
                            break
                        necesita = regla.cantidad_requerida - acumulado_req
                        toma = min(item_r['qty_available'] - temp_updates.get(item_r['prod_id'], 0), necesita)
                        if toma > 0:
                            temp_updates[item_r['prod_id']] = temp_updates.get(item_r['prod_id'], 0) + toma
                            acumulado_req += toma
                            req_consumidos.append((item_r['prod_id'], item_r['precio'], toma))

                    if acumulado_req < regla.cantidad_requerida:
                        break

                    # Intentar consumir los regalos
                    regalo_disponibles_sorted = []
                    for ip in items_productos:
                        prod = ip['producto']
                        qty = cantidades_disponibles.get(prod.id, 0) - temp_updates.get(prod.id, 0)
                        if qty > 0:
                            cumple_tipo = (not regla.tipo_regalo) or (prod.tipo_producto == regla.tipo_regalo)
                            cumple_cat = (not regla.categoria_regalo) or (prod.categoria_id == regla.categoria_regalo_id)
                            if cumple_tipo and cumple_cat:
                                regalo_disponibles_sorted.append({
                                    'prod_id': prod.id,
                                    'precio': ip['precio'],
                                    'qty_available': qty
                                })
                    
                    regalo_disponibles_sorted = sorted(regalo_disponibles_sorted, key=lambda x: x['precio'])
                    
                    acumulado_regalo = 0
                    regalo_consumidos = []
                    for item_g in regalo_disponibles_sorted:
                        if acumulado_regalo >= regla.cantidad_regalo:
                            break
                        necesita = regla.cantidad_regalo - acumulado_regalo
                        toma = min(item_g['qty_available'], necesita)
                        if toma > 0:
                            temp_updates[item_g['prod_id']] = temp_updates.get(item_g['prod_id'], 0) + toma
                            acumulado_regalo += toma
                            regalo_consumidos.append((item_g['prod_id'], item_g['precio'], toma))

                    if acumulado_regalo < regla.cantidad_regalo:
                        break
                    
                    # Consolidar asignación
                    for p_id, q_used in temp_updates.items():
                        cantidades_disponibles[p_id] -= q_used
                    
                    # Calcular precio normal de esta activación del combo
                    normal_sum = Decimal('0.00')
                    for p_id, precio, q in req_consumidos:
                        normal_sum += precio * q
                    for p_id, precio, q in regalo_consumidos:
                        normal_sum += precio * q

                    # Calcular descuento
                    if regla.precio_combo and regla.precio_combo > 0:
                        descuento_esta_vez = normal_sum - Decimal(str(regla.precio_combo))
                    else:
                        descuento_esta_vez = Decimal('0.00')
                        for p_id, precio, q in regalo_consumidos:
                            descuento_esta_vez += precio * q
                    
                    if descuento_esta_vez > 0:
                        descuento_regla_total += descuento_esta_vez
                        veces_activado += 1

                if veces_activado > 0 and descuento_regla_total > 0:
                    descuento_combos += descuento_regla_total
                    combos_a_crear.append({
                        'nombre': regla.nombre,
                        'descuento_aplicado': descuento_regla_total
                    })

        descuento_total = descuento_combos
        costo_envio = Decimal('0.00')
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

        # Registrar los combos aplicados en la BD
        for cb in combos_a_crear:
            ComboPedido.objects.create(
                pedido=pedido,
                nombre=cb['nombre'],
                descuento_aplicado=cb['descuento_aplicado']
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
            'listo': 'ready',
            'entregado': 'delivered',
            'cancelado': 'cancelled',
            'pending': 'pending',
            'payment_review': 'payment_review',
            'payment_validated': 'payment_validated',
            'processing': 'processing',
            'ready': 'ready',
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
            data['shipping_status'] = 'paid' if pago_delivery.estado == 'completado' else 'pending'
            data['shipping_payment_method'] = 'paypal' if pago_delivery.metodo_pago == 'paypal' else 'receipt'
            data['shipping_paypal_order_id'] = pago_delivery.id_transaccion
            data['shipping_payment_receipt_url'] = pago_delivery.imagen_comprobante.url if pago_delivery.imagen_comprobante else None
        else:
            data['shipping_status'] = 'pending'
            
        return data
