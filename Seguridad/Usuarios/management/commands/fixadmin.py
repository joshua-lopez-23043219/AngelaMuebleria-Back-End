from django.core.management.base import BaseCommand
from Seguridad.Usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Actualiza todos los superusuarios para que tengan el rol de admin y no requieran confirmación de correo'

    def handle(self, *args, **kwargs):
        superusers = Usuario.objects.filter(is_superuser=True)
        count = superusers.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No se encontraron superusuarios.'))
            return
            
        for user in superusers:
            user.rol = 'admin'
            user.email_verificado = True
            user.save()
            
        self.stdout.write(self.style.SUCCESS(f'Éxito: Se han actualizado {count} superusuarios con el rol de admin.'))
