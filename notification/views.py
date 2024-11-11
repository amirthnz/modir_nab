from django.shortcuts import render
from notification.models import Notif

# Create your views here.
def list(request):
    notifications = Notif.objects.all().order_by('-created')

    context = {
        'notifications':notifications
    }

    return render(request, 'notification/notification_list.html', context)