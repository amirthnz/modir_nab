from django.db import models

# Create your models here.
class GiftItem(models.Model):

    class TypeOfGift(models.TextChoices):
        FILE = 'FI', 'File'
        VIDEO = 'VI', 'Video'

    title = models.CharField(max_length=255, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیحات')
    download_count = models.IntegerField(default=0, null=True, blank=True, verbose_name='تعداد دفعات بارگیری')
    content = models.FileField(upload_to='gifts/', null=True, blank=True, verbose_name='ویدئو یا فایل دانلود')
    gift_type = models.CharField(max_length=2, choices=TypeOfGift.choices, default=TypeOfGift.FILE, verbose_name='نوع هدیه')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'هدیه'
        verbose_name_plural = 'هدایا'
