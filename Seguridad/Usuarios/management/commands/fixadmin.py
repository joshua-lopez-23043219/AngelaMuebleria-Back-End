from django.core.management.base import BaseCommand
from Seguridad.Usuarios.models import Usuario

class Command(BaseCommand):
    help = 'Actualiza superusuarios o un usuario específico por email para que sean admins y estén activos'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email del usuario específico a activar/hacer admin')

    def handle(self, *args, **options):
        email = options.get('email')
        
        if email:
            users = Usuario.objects.filter(email=email)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f'No se encontró el usuario con email: {email}'))
                return
        else:
            users = Usuario.objects.filter(is_superuser=True)
            
        count = users.count()
        if count == 0:
            self.stdout.write(self.style.WARNING('No se encontraron usuarios para procesar.'))
            return
            
        for user in users:
            user.rol = 'admin'
            user.email_verificado = True
            user.is_active = True  # Forzar activación por si acaso
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario {user.email} actualizado: Rol=admin, Activo=True'))
            
        self.stdout.write(self.style.SUCCESS(f'Proceso completado. {count} usuarios afectados.'))
