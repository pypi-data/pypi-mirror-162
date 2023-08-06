from django.http import HttpResponse
from . models import SchedulerLock


def index(request):
    x = SchedulerLock.objects.all()
    print(x)
    return HttpResponse("Hello, World DISCOVERY")
