from rest_framework import serializers
from .models import Chat


class ScheduleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'user']


