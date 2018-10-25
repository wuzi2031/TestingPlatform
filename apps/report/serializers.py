from rest_framework import serializers

from case.serializers import CaseSerializer
from .models import TaskExecuteInfo


class TaskExecuteInfoSerializer(serializers.ModelSerializer):
    case = CaseSerializer(read_only=True)

    class Meta:
        model = TaskExecuteInfo
        fields = "__all__"
