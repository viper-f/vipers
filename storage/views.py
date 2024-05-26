import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from storage.models import StorageRecord

@csrf_exempt
def record_put(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "invalid json"})

        if 'board_id' not in data or 'key' not in data or 'value' not in data:
            return JsonResponse({"error": "forum, key and value are required values"})

        if 'user_id' in data:
            user_id = data.get("user_id")
        else:
            user_id = None

        record = StorageRecord.objects.filter(board_id=data.get("board_id"), user_id=data.get("user_id"),
                                              key=data.get("key"))

        if 'type' in data:
            type = data.get("type")
        else:
            if record is not None:
                type = record.type
            else:
                type = "text"

        if type == "json":
            value = json.dumps(data.get('value'))
        else:
            value = data.get('value')

        # create
        if record is None:
            record = StorageRecord(
                board_id=data.get("board_id"),
                user_id=user_id,
                key=data.get('key'),
                value=value,
                type=type
            )
            record.save()
            return JsonResponse({"status": "success"})

        # update
        else:
            record = record.first()
            record.value = value
            record.type = type
            record.save()
            return JsonResponse({"status": "success"})

def record_get(request):
    if request.method == "GET":

        data = request.GET
        record = StorageRecord.objects.filter(board_id=data.get("board_id"), user_id=data.get("user_id"),
                                              key=data.get("key")).first()
        if record is None:
            return JsonResponse({"error": "record not found"}, status=400)

        print(record.value)

        if record.type == "json":
            response = {
                record.key: json.loads(record.value)
            }
        else:
            response = {
                record.key: record.value
            }

        return JsonResponse(response)

