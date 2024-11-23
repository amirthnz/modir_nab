from django.urls import path
from catalog import views

app_name = 'catalog'

urlpatterns = [
    path('categories/', views.list_category, name='cat_list'), # List categories
    path('categories/add/', views.add_category, name='cat_add'), # Add category
    path('categories/edit/<int:pk>/', views.edit_category, name='cat_edit'), # Edit category
    path('categories/delete/<pk>/', views.delete_category, name='cat_delete'), # Delete category

    path('products/', views.list_product, name='product_list'), # List products
    path('products/add/', views.add_product, name='product_add'), # Add product
    path('products/edit/<int:pk>/', views.edit_product, name='product_edit'), # Edit product
    path('products/delete/<pk>/', views.delete_product, name='product_delete'), # Delete product
]
