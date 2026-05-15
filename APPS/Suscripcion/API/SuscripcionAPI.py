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
