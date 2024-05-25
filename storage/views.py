from django.http import JsonResponse
from storage.models import StorageRecord

def record_put(request):
    if request.method == "POST":
        data = request.POST

        if 'user_id' in data:
            user_id = data.get("user_id")
        else:
            user_id = None

        # create
        if 'record_id' not in data:
            record = StorageRecord(
                board_id=data.get("board_id"),
                user_id=user_id,
                key=data.get('key'),
                value=data.get('value')
            )
            record.save()
            return JsonResponse({"status": "success"})

        # update
        else:
            record = StorageRecord.objects.filter(board_id=data.get("board_id"), user_id=data.get("user_id"), key=data.get("key"))

            if record is None:
                return JsonResponse({"error": "record not found"})

            record = StorageRecord(
                value=data.get('value')
            )
            record.save()
            return JsonResponse({"status": "success"})

def record_get(request):
    if request.method == "GET":
        data = request.GET

    record = StorageRecord.objects.filter(board_id=data.get("board_id"), user_id=data.get("user_id"),
                                          key=data.get("key"))

    if record is None:
        return JsonResponse({"error": "record not found"})

    return JsonResponse({record.key: record.value})

