from django.db import models

from APPS import Pedidos


class Pago(models.Model):
    OPCIONES_METODO = (
        ('paypal', 'PayPal'),
        ('tarjeta', 'Tarjeta de Crédito / Débito'),
        ('transferencia', 'Transferencia Bancaria / Pago Móvil'),
    )
    OPCIONES_ESTADO = (
        ('pendiente', 'Pendiente de Verificación'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido / Rechazado'),
        ('reembolsado', 'Reembolsado'),
    )
    OPCIONES_TIPO_PAGO = (
        ('productos', 'Pago de Muebles'),
        ('delivery', 'Pago de Delivery/Envío'),
    )

    # CAMBIO CLAVE: Ahora es un ForeignKey, permitiendo varios pagos para un solo pedido.
    # Además, cambiamos el related_name a 'pagos' (en plural)
    pedido = models.ForeignKey('Pedidos.Pedido', on_delete=models.CASCADE, related_name='pagos')

    # NUEVO: ¿Qué está pagando el cliente en esta transacción?
    tipo_pago = models.CharField(max_length=20, choices=OPCIONES_TIPO_PAGO, default='productos')

    metodo_pago = models.CharField(max_length=20, choices=OPCIONES_METODO)
    id_transaccion = models.CharField(max_length=255, blank=True, null=True)
    imagen_comprobante = models.ImageField(upload_to='comprobantes/%Y/%m/', blank=True, null=True)

    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default='pendiente')

    creado_en = models.DateTimeField(auto_now_add=True)
    verificado_en = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Pago {self.id} ({self.get_tipo_pago_display()}) - Pedido {self.pedido.id}"
# Create your models here.
