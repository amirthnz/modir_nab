from django.urls import path
from gift import views

app_name = 'gift'

urlpatterns = [
    path('', views.gift_list, name='gift_list'),
    path('add/', views.gift_add, name='gift_add'),
    path('edit/<id>/', views.gift_detail, name='edit_gift'),
    path('delete/<id>/', views.gift_delete, name='gift_delete')
]
