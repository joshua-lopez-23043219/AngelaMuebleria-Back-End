from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
import threading

from Seguridad.Usuarios.API.SerializerUsuario import SerializerUsuario
from Seguridad.Usuarios.models import Usuario
from Seguridad.throttling import AuthRateThrottle, EmailSpamRateThrottle


class UsuarioViewsSet (ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = SerializerUsuario

    def get_queryset(self):
        user = self.request.user
        if not user or user.is_anonymous:
            return Usuario.objects.none()
        
        is_admin = user.is_superuser or (hasattr(user, 'rol') and user.rol == 'admin')
        if is_admin:
            return Usuario.objects.all().order_by('-date_joined')
            
        return Usuario.objects.filter(pk=user.pk)

    def get_permissions(self):
        if self.action == 'create':
            return []
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        user = self.request.user
        is_admin = user.is_superuser or (hasattr(user, 'rol') and user.rol == 'admin')
        if not is_admin:
            # Prevent non-admin users from escalating privileges or changing status
            original = self.get_object()
            serializer.save(
                rol=original.rol,
                is_active=original.is_active,
                email_verificado=original.email_verificado
            )
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def ban_user(self, request, pk=None):
        if not (request.user and request.user.is_authenticated and (request.user.is_superuser or request.user.rol == 'admin')):
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
            
        user = self.get_object()
        # Toggle is_active status or set based on request body
        is_active_val = request.data.get('is_active', False)
        user.is_active = is_active_val
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def activar_manual(self, request, pk=None):
        if not (request.user and request.user.is_authenticated and (request.user.is_superuser or request.user.rol == 'admin')):
            return Response({"error": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
            
        user = self.get_object()
        user.is_active = True
        user.email_verificado = True
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_throttles(self):
        if self.action == 'create':
            return [AuthRateThrottle()]
        elif self.action in ['recuperar_contrasena', 'restablecer_contrasena']:
            return [EmailSpamRateThrottle()]
        return super().get_throttles()

    @action(detail=False, methods=['get'], url_path='activar/(?P<uidb64>[^/.]+)/(?P<token>[^/.]+)')
    def activar(self, request, uidb64=None, token=None):
        try:
            # 1. Decodificamos el ID del usuario
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            user = None
        from django.http import HttpResponseRedirect
        
        # 2. Verificamos si el token es válido o si el usuario ya está verificado y activo
        if user is not None and (default_token_generator.check_token(user, token) or (user.is_active and user.email_verificado)):
            user.is_active = True  # Activamos al usuario
            user.email_verificado = True
            user.save()
            # Redirigimos al frontend con un mensaje de éxito
            return HttpResponseRedirect("https://angelamuebleria.business/?activated=true")

        else:
            # Redirigimos al frontend con un mensaje de error
            return HttpResponseRedirect("https://angelamuebleria.business/?activated=false")

    @action(detail=False, methods=['post'], url_path='recuperar_contrasena')
    def recuperar_contrasena(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {"error": "El correo electrónico es requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "No se encontró ningún usuario registrado con este correo electrónico."},
                status=status.HTTP_404_NOT_FOUND
            )

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Enlace del frontend para restablecer contraseña
        enlace_restablecimiento = f"https://angelamuebleria.business/?action=reset-password&uid={uid}&token={token}"
        
        asunto = "Restablece tu contraseña - Mueblería Ángela"
        mensaje_texto = f"Hola {user.username},\n\nHemos recibido una solicitud para restablecer tu contraseña en Mueblería Ángela. Para cambiarla, haz clic en el siguiente enlace:\n\n{enlace_restablecimiento}\n\nSi no solicitaste este cambio, por favor ignora este correo."
        
        mensaje_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                <h2 style="color: #c5a059; text-align: center; font-family: 'Georgia', serif;">Restablece tu Contraseña</h2>
                <p>Hola <strong>{user.username}</strong>,</p>
                <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en Mueblería Ángela.</p>
                <p>Para elegir una nueva contraseña, haz clic en el siguiente botón:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{enlace_restablecimiento}" style="background-color: #c5a059; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Restablecer Contraseña</a>
                </div>
                <p style="font-size: 12px; color: #7f8c8d; text-align: center;">Si el botón no funciona, copia y pega el siguiente enlace en tu navegador:</p>
                <p style="font-size: 12px; color: #7f8c8d; text-align: center; word-break: break-all;">{enlace_restablecimiento}</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;" />
                <p style="font-size: 11px; color: #95a5a6; text-align: center;">Si no solicitaste este cambio, puedes ignorar este correo de forma segura.</p>
            </body>
        </html>
        """

        def send_email_thread():
            try:
                send_mail(
                    subject=asunto,
                    message=mensaje_texto,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=mensaje_html,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error enviando correo de recuperación: {e}")

        threading.Thread(target=send_email_thread).start()
        
        return Response(
            {"detail": "Se ha enviado un correo electrónico con instrucciones para restablecer su contraseña."},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='restablecer_contrasena')
    def restablecer_contrasena(self, request):
        uidb64 = request.data.get('uidb64')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not uidb64 or not token or not new_password:
            return Response(
                {"error": "Todos los campos son requeridos (uidb64, token, new_password)."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
            user = None
            
        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response(
                {"detail": "Contraseña restablecida exitosamente."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "El enlace de restablecimiento es inválido o ha expirado."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='enviar_correo_masivo')
    def enviar_correo_masivo(self, request):
        if not request.user or request.user.is_anonymous or request.user.rol != 'admin':
            return Response(
                {"error": "No tienes permisos de administrador para realizar esta acción."},
                status=status.HTTP_403_FORBIDDEN
            )

        subject = request.data.get('subject')
        title = request.data.get('title')
        message = request.data.get('message')

        if not subject or not title or not message:
            return Response(
                {"error": "Los campos 'subject', 'title' y 'message' son requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Obtener correos únicos de clientes y suscriptores
        from APPS.Suscripcion.models import Suscriptor
        
        emails_usuarios = Usuario.objects.filter(rol='cliente', email__isnull=False).exclude(email='').values_list('email', flat=True)
        emails_suscriptores = Suscriptor.objects.all().values_list('email', flat=True)
        
        unique_emails = set(list(emails_usuarios) + list(emails_suscriptores))
        if not unique_emails:
            return Response(
                {"error": "No hay ningún cliente o suscriptor registrado en la base de datos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Obtener productos activos para el catálogo en el correo
        from APPS.Producto.models import Producto
        productos_activos = Producto.objects.filter(esta_activo=True)[:10]  # Limitamos a 10 productos para no saturar el correo
        
        # 3. Formatear la lista de productos en HTML
        productos_html = ""
        for prod in productos_activos:
            img_url = "https://picsum.photos/seed/mueble/300/200"
            if prod.url_miniatura:
                img_url = f"https://api.angelamuebleria.business{prod.url_miniatura.url}"
                
            desc_text = prod.descripcion[:100] + "..." if prod.descripcion and len(prod.descripcion) > 100 else (prod.descripcion or "")
            
            productos_html += f"""
            <div style="border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; margin-bottom: 20px; background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                        <td width="35%" style="padding: 15px; vertical-align: top;">
                            <img src="{img_url}" alt="{prod.nombre}" style="width: 100%; max-width: 150px; height: auto; border-radius: 8px; object-fit: cover;" />
                        </td>
                        <td width="65%" style="padding: 15px 15px 15px 0; vertical-align: top; text-align: left;">
                            <h4 style="margin: 0 0 5px 0; color: #2c3e50; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 16px;">{prod.nombre}</h4>
                            <p style="margin: 0 0 10px 0; color: #7f8c8d; font-size: 12px; line-height: 1.4;">{desc_text}</p>
                            <div style="font-weight: bold; color: #c5a059; font-size: 16px; margin-bottom: 10px;">C$ {float(prod.precio_base):,.2f}</div>
                            <a href="https://angelamuebleria.business/" style="background-color: #2c3e50; color: white; padding: 6px 12px; text-decoration: none; border-radius: 6px; font-size: 11px; font-weight: bold; display: inline-block;">Ver Detalle</a>
                        </td>
                    </tr>
                </table>
            </div>
            """

        # 4. Crear el HTML completo del correo
        mensaje_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
                <div style="background-color: #2c3e50; padding: 20px; text-align: center; border-top-left-radius: 12px; border-top-right-radius: 12px;">
                    <h1 style="color: #ffffff; margin: 0; font-family: 'Georgia', serif; font-size: 24px;">Angela Mueblería</h1>
                    <p style="color: #c5a059; margin: 5px 0 0 0; font-size: 12px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase;">Diseño y Tradición Nicaragüense</p>
                </div>
                
                <div style="background-color: #ffffff; padding: 30px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; border: 1px solid #eee; border-top: none; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    <h2 style="color: #2c3e50; font-size: 20px; margin-top: 0;">{title}</h2>
                    <p style="color: #555; font-size: 14px; line-height: 1.6; white-space: pre-line;">{message}</p>
                    
                    {f'<h3 style="color: #2c3e50; border-bottom: 2px solid #c5a059; padding-bottom: 8px; margin-top: 30px; margin-bottom: 20px; font-family: Georgia, serif;">Catálogo Especial</h3>' if productos_html else ''}
                    {productos_html}
                    
                    <div style="text-align: center; margin-top: 30px; margin-bottom: 20px;">
                        <a href="https://angelamuebleria.business/" style="background-color: #c5a059; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 14px; display: inline-block; box-shadow: 0 4px 6px rgba(197,160,89,0.2);">Visitar Catálogo Completo</a>
                    </div>
                    
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;" />
                    <p style="font-size: 11px; color: #95a5a6; text-align: center; line-height: 1.4;">
                        Este es un correo automático enviado a los clientes y suscriptores de Angela Mueblería.<br />
                        Masatepe, Masaya, Nicaragua.
                    </p>
                </div>
            </body>
        </html>
        """

        # Enviar correos de manera asíncrona en un hilo
        def send_bulk_emails():
            for recipient_email in unique_emails:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient_email],
                        html_message=mensaje_html,
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error enviando correo masivo a {recipient_email}: {e}")

        threading.Thread(target=send_bulk_emails).start()

        return Response(
            {"detail": f"Correo masivo en proceso de envío a {len(unique_emails)} destinatarios."},
            status=status.HTTP_200_OK
        )