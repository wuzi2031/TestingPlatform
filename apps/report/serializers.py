from rest_framework import serializers

from .models import TaskExecuteInfo


class TaskExecuteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskExecuteInfo
        fields = "__all__"
