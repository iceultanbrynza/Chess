from rest_framework import serializers

from .models import Player

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = (
            'username',
            'password'
        )