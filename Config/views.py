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
    
    # Validation checks
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'glb', 'gltf'}
    if '.' not in file.name:
        return Response({"error": "File has no extension"}, status=status.HTTP_400_BAD_REQUEST)
        
    ext = file.name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        return Response({"error": f"Extension .{ext} is not allowed"}, status=status.HTTP_400_BAD_REQUEST)
        
    max_size = 25 * 1024 * 1024  # 25 MB
    if file.size > max_size:
        return Response({"error": "File size exceeds the 25MB limit"}, status=status.HTTP_400_BAD_REQUEST)
        
    upload_type = request.POST.get('type', 'general')
    
    # Generate unique filename
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
