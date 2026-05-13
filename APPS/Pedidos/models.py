from django.db import models
from django.conf import settings


class Pedido(models.Model):
    OPCIONES_ESTADO = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    OPCIONES_ENTREGA = (
        ('local', 'Retiro en el local'),
        ('domicilio', 'Envío a domicilio'),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    metodo_entrega = models.CharField(max_length=20, choices=OPCIONES_ENTREGA, default='domicilio')

    # Desglose financiero actualizado
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # NUEVO: Costo del flete/delivery
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # El total general = (subtotal - descuento_total) + costo_envio
    total = models.DecimalField(max_digits=10, decimal_places=2)

    estado = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.id} - Usuario ID: {self.usuario.id}"

# Create your models here.
