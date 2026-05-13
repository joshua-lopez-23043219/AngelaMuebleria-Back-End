from django.db import models


class Municipio(models.Model):
    nombre = models.CharField(max_length=100)

    # Llave foránea hacia la app Departamento
    departamento = models.ForeignKey('Departamento.Departamento', on_delete=models.CASCADE, related_name='municipios')



    def __str__(self):
        return f"{self.nombre}, {self.departamento.nombre}"

# Create your models here.
