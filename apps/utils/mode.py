from django.core.serializers import serialize
import json


def modelToJson(model):
    json_obj = json.loads(serialize("json", [model])[1:-1])
    return json_obj
