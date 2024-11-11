from django.db import models
from bot.models import Customer
from django_jalali.db import models as jmodels
import jdatetime

# Create your models here.
class Notif(models.Model):
    from_user = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications', verbose_name='کاربر')
    message = models.TextField(verbose_name='پیام')
    created = jmodels.jDateTimeField(verbose_name='تاریخ ایجاد')

    def __str__(self):
        return f'{self.from_user} {self.message}'

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = jdatetime.datetime.now()
        return super(Notif, self).save(*args, **kwargs)