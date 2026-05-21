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
    OPCIONES_TIPO = (
        ('silla', 'Silla'),
        ('mesa', 'Mesa'),
        ('sofa', 'Sofá'),
        ('cama', 'Cama'),
        ('armario', 'Armario/Gabinete'),
        ('otro', 'Otro'),
    )

    nombre = models.CharField(max_length=255, help_text="Nombre descriptivo del combo")
    
    # Requerimiento
    tipo_requerido = models.CharField(
        max_length=20, 
        choices=OPCIONES_TIPO, 
        default='silla',
        help_text="Tipo de producto requerido para activar el combo"
    )
    categoria_requerida = models.ForeignKey(
        'Categoria.Categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='combos_requeridos',
        help_text="Categoría específica requerida (opcional)"
    )
    cantidad_requerida = models.PositiveIntegerField(
        default=4,
        help_text="Cantidad mínima del producto requerido"
    )

    # Regalo
    tipo_regalo = models.CharField(
        max_length=20,
        choices=OPCIONES_TIPO,
        default='mesa',
        help_text="Tipo de producto regalado"
    )
    categoria_regalo = models.ForeignKey(
        'Categoria.Categoria',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='combos_regalo',
        help_text="Categoría específica de regalo (opcional)"
    )
    cantidad_regalo = models.PositiveIntegerField(
        default=1,
        help_text="Cantidad de productos regalados"
    )

    activo = models.BooleanField(default=True)
    precio_combo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Precio fijo para el combo (si se establece, sustituye el regalo gratuito)"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} (Compra {self.cantidad_requerida} -> Regalo {self.cantidad_regalo})"

# Create your models here.
