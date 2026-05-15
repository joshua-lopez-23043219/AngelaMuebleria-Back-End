import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
    file = request.FILES['file']
    upload_type = request.POST.get('type', 'general')
    
    # Generate unique filename
    ext = file.name.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = f"uploads/{upload_type}/{filename}"
    
    # Save the file using default storage
    saved_path = default_storage.save(path, file)
    
    # Generate URL
    url = request.build_absolute_uri(default_storage.url(saved_path))
    
    # We return the relative path as well, so it can be saved in DB
    return Response({
        "url": default_storage.url(saved_path),
        "path": saved_path
    }, status=status.HTTP_201_CREATED)
