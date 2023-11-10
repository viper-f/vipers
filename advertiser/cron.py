from advertiser.models import ScheduleItem
from datetime import date

def scheduled_job():
    today = date.today()

    scheduled_item = ScheduleItem.objects.filter(active=True, last_run < )