import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from storage.models import StorageRecord

@csrf_exempt
def record_put(request):
    headers = {"Access-Control-Allow-Origin": ''}
    if request.META['HTTP_REFERER'] in ['http://localhost', 'https://kingscross.f-rpg.me']:
        headers = {"Access-Control-Allow-Origin": request.META['HTTP_REFERER']}

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "invalid json"}, headers=headers)

        if 'board_id' not in data or 'key' not in data or 'value' not in data:
            return JsonResponse({"error": "forum, key and value are required values"}, headers=headers)

        if 'user_id' in data:
            user_id = data.get("user_id")
        else:
            user_id = None

        if 'type' in data:
            type = data.get("type")
        else:
            type = "text"

        # create
        if 'record_id' not in data:
            record = StorageRecord(
                board_id=data.get("board_id"),
                user_id=user_id,
                key=data.get('key'),
                value=data.get('value'),
                type=type
            )
            record.save()
            return JsonResponse({"status": "success"}, headers=headers)

        # update
        else:
            record = StorageRecord.objects.filter(board_id=data.get("board_id"), user_id=data.get("user_id"), key=data.get("key"))

            if record is None:
                return JsonResponse({"error": "record not found"}, headers=headers)

            record = StorageRecord(
                value=data.get('value'),
                type=type
            )
            record.save()
            return JsonResponse({"status": "success"}, headers=headers)

def record_get(request):
    headers = {"Access-Control-Allow-Origin": ''}
    if request.META['HTTP_REFERER'] in ['http://localhost', 'https://kingscross.f-rpg.me']:
        headers = {"Access-Control-Allow-Origin": request.META['HTTP_REFERER']}

    if request.method == "GET":

        data = request.GET
        record = StorageRecord.objects.filter(board_id=data.get("board_id"), user_id=data.get("user_id"),
                                              key=data.get("key")).first()

        if record is None:
            return JsonResponse({"error": "record not found"}, headers=headers)

        if record.type == "json":
            response = {
                record.key: json.loads(record.value)
            }
        else:
            response = {
                record.key: record.value
            }

        return JsonResponse(response, headers=headers)

