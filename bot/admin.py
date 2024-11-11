from django.contrib import admin
from bot.models import Customer, Telebot, Post

# Register your models here.

admin.site.register(Customer)
admin.site.register(Post)
class RobotAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Check if an instance already exists
        if Telebot.objects.exists():
            return False
        return True

admin.site.register(Telebot, RobotAdmin)