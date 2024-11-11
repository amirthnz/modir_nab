from django.urls import path
from bot import views

app_name = 'bot'

urlpatterns = [
    path('users/', views.user_list, name='list'),
    path('posts/', views.post_list, name='posts'),
    path('posts/add/', views.post_add, name='add_post'),
    path('posts/<id>/', views.post_edit, name='edit_post'),
    path('posts/delete/<id>/', views.post_delete, name='post_delete'),
    path('broadcast/', views.broadcast, name='broadcast'),
    path('user/<int:id>/', views.user_detail, name='detail'),
    path('bot/add/', views.add_bot, name='add_bot'),
    path('bot/', views.edit_bot, name='edit_bot'),
    path('webhook/', views.TelegramWebhookAPI.as_view(), name='webhook'),
]
