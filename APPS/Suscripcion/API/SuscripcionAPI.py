from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from APPS.Suscripcion.API.SerializerSuscripcion import SerializerSuscriptor
from APPS.Suscripcion.models import Suscriptor


class SuscripcionViewsSet(ModelViewSet):
    queryset = Suscriptor.objects.all()
    serializer_class = SerializerSuscriptor
    
    def get_permissions(self):
        # Permitir que cualquiera se suscriba o valide códigos
        if self.action in ['create', 'validate_discount']:
            return [AllowAny()]
        # Solo admin puede ver la lista de suscriptores o borrarlos
        return [IsAdminUser()]

    @action(detail=False, methods=['post'], url_path='validate-discount')
    def validate_discount(self, request):
        codigo = request.data.get('code')
        if not codigo:
            return Response({"error": "Código no proporcionado."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            suscriptor = Suscriptor.objects.get(codigo_descuento=codigo)
            if suscriptor.fue_usado:
                return Response({"error": "Este código de descuento ya fue utilizado."}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({
                "valid": True,
                "percentage": float(suscriptor.porcentaje_descuento),
                "code": suscriptor.codigo_descuento
            }, status=status.HTTP_200_OK)
            
        except Suscriptor.DoesNotExist:
            return Response({"error": "El código de descuento no existe o es inválido."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='generar-cupones')
    def generar_cupones(self, request):
        cantidad = int(request.data.get('cantidad', 1))
        porcentaje = float(request.data.get('porcentaje', 10.00))
        
        if cantidad < 1 or cantidad > 100:
            return Response({"error": "Cantidad inválida (máximo 100 cupones a la vez)."}, status=status.HTTP_400_BAD_REQUEST)
            
        generated_codes = []
        import string
        import random
        
        for _ in range(cantidad):
            # Create unique code
            while True:
                caracteres = string.ascii_uppercase + string.digits
                codigo_aleatorio = ''.join(random.choice(caracteres) for i in range(6))
                code = f"DESC-{codigo_aleatorio}"
                # Check uniqueness in db
                if not Suscriptor.objects.filter(codigo_descuento=code).exists():
                    break
                    
            # Create dummy email
            dummy_email = f"coupon-{codigo_aleatorio}@angelamuebleria.business"
            # Check uniqueness of email (just in case)
            while Suscriptor.objects.filter(email=dummy_email).exists():
                codigo_aleatorio = ''.join(random.choice(caracteres) for i in range(6))
                dummy_email = f"coupon-{codigo_aleatorio}@angelamuebleria.business"

            # Save coupon using Suscriptor model
            suscriptor = Suscriptor(
                email=dummy_email,
                codigo_descuento=code,
                porcentaje_descuento=porcentaje,
                fue_usado=False
            )
            suscriptor.save()
            generated_codes.append({
                "code": code,
                "percentage": porcentaje
            })
            
        return Response({"detail": f"Se generaron {cantidad} cupones exitosamente.", "coupons": generated_codes}, status=status.HTTP_200_OK)

