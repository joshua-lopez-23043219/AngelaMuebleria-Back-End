from django.db import models

from APPS import Pedidos


class ComboPedido(models.Model):
    # Llave foránea hacia la app Pedido
    pedido = models.ForeignKey('Pedidos.Pedido', on_delete=models.CASCADE, related_name='combos')
    nombre = models.CharField(max_length=255, help_text="Ej: Combo 4 Sillas + Mesa")
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - Pedido {self.pedido.id}"


class ReglaCombo(models.Model):
    nombre = models.CharField(max_length=255, help_text="Nombre descriptivo del combo")
    
    # Requerimiento
    producto_requerido = models.ForeignKey(
        'Producto.Producto',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='combos_requeridos',
        help_text="Producto específico requerido para activar el combo"
    )
    cantidad_requerida = models.PositiveIntegerField(
        default=4,
        help_text="Cantidad mínima del producto requerido"
    )

    # Asociación (antes regalo)
    producto_asociado = models.ForeignKey(
        'Producto.Producto',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='combos_asociados',
        help_text="Producto específico asociado que completa el combo"
    )
    cantidad_asociado = models.PositiveIntegerField(
        default=1,
        help_text="Cantidad de productos asociados"
    )

    activo = models.BooleanField(default=True)
    precio_combo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Precio fijo para el combo"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            return f"{self.nombre} ({self.cantidad_requerida} x {self.producto_requerido.nombre} + {self.cantidad_asociado} x {self.producto_asociado.nombre} por C$ {self.precio_combo})"
        except Exception:
            return f"{self.nombre}"
