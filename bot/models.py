from django.db import models
from django_jalali.db import models as jmodels
import jdatetime
import mimetypes


class Customer(models.Model):
    chat_id = models.CharField(max_length=255, primary_key=True, verbose_name='آی دی چت')
    first_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام')
    last_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام خانوادگی')
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name='نام کاربری')
    has_username = models.BooleanField(default=False, verbose_name='نام کاربری دارد')
    has_recieved_gift = models.BooleanField(default=False, verbose_name='هدیه دریافت کرده')
    phone_number = models.CharField(max_length=18, null=True, blank=True, verbose_name='شماره همراه')
    has_phone_number = models.BooleanField(default=False, verbose_name='شماره همراه دارد')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, verbose_name='عکس پروفایل')
    otp = models.CharField(max_length=6, null=True, blank=True, verbose_name='کد یکبار مصرف')
    created = jmodels.jDateTimeField(verbose_name='تاریخ ایجاد')
    modified = jmodels.jDateField(verbose_name='تاریخ ویرایش')

    def __str__(self) -> str:
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name:
            return f'{self.first_name}'

        return self.chat_id


    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.chat_id:
            self.created = jdatetime.datetime.now()
        self.modified = jdatetime.datetime.now()
        return super(Customer, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'کاربر تلگرام'
        verbose_name_plural = 'کاربران تلگرام'


class Telebot(models.Model):
    title = models.CharField(max_length=100, verbose_name='عنوان')
    token = models.CharField(max_length=300, verbose_name='توکن')
    welcome_message = models.TextField(verbose_name='پیام خوش آمدگویی')
    welcome_picture = models.ImageField(upload_to='media/pictures/', verbose_name='تصویر خوش آمدگویی')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'ربات'
        verbose_name_plural = 'ربات ها'


class Post(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    title = models.CharField(max_length=255, verbose_name='عنوان')
    content = models.TextField(verbose_name='محتوا')
    photo = models.ImageField(upload_to='media/posts/', null=True, blank=True, verbose_name='تصویر شاخص')
    media = models.FileField(upload_to='media/posts/', null=True, blank=True, verbose_name='تصویر شاخص')
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPE_CHOICES, default='image')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Automatically set media_type based on the uploaded file
        file_type, _ = mimetypes.guess_type(self.media.name)

        if file_type:
            if file_type.startswith('image/'):
                self.media_type = 'image'
            elif file_type.startswith('video/'):
                self.media_type = 'video'
            else:
                # Optional: Handle unknown types if necessary
                self.media_type = 'unknown'  # Set to a default if not an image or video
        else:
            # Optional: Handle cases where the file type cannot be determined
            self.media_type = 'unknown'  # Set to a default if not an image or video

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'صفحه'
        verbose_name_plural = 'صفحات'