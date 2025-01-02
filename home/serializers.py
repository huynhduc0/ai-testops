from rest_framework import serializers
from .models import Canvas, Element

class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = ['id', 'type', 'content', 'image', 'x', 'y']

class CanvasSerializer(serializers.ModelSerializer):
    elements = ElementSerializer(many=True, required=False)

    class Meta:
        model = Canvas
        fields = ['id', 'name', 'owner', 'created_at', 'updated_at', 'elements']
        read_only_fields = ['owner']

    def create(self, validated_data):
        elements_data = validated_data.pop('elements', [])
        canvas = Canvas.objects.create(**validated_data)
        for element_data in elements_data:
            Element.objects.create(canvas=canvas, **element_data)
        return canvas
