from django.db import models
from django.contrib.auth.models import User

class Canvas(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Element(models.Model):
    CANVAS_ELEMENT_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
    ]
    canvas = models.ForeignKey(Canvas, related_name='elements', on_delete=models.CASCADE)
    type = models.CharField(choices=CANVAS_ELEMENT_TYPES, max_length=10)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='canvas_images/', blank=True, null=True)
    x = models.IntegerField()
    y = models.IntegerField()
