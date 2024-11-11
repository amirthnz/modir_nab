from django.urls import path
from notification import views

app_name = 'notification'

urlpatterns = [
    path('', views.list, name='notif_list'),
]
