from django.contrib import admin
from catalog import models


admin.site.register(models.Category)

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'link_to_website')
    search_fields = ('title', 'description')