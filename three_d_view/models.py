from django.db import models
from django.contrib.auth.models import User

class Project3D(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # 3D Model File (.glb, .gltf, etc.)
    model_file = models.FileField(upload_to='3d_models/')
    
    # Coordinates for placement
    latitude = models.FloatField(default=25.2048) # Dubai default
    longitude = models.FloatField(default=55.2708)
    altitude = models.FloatField(default=0.0) # Height in meters
    
    # Orientation/Scale
    heading = models.FloatField(default=0.0) # Rotation around Z (0-360)
    scale = models.FloatField(default=1.0)
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
