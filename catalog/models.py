from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='عنوان')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='دسته بندی')
    title = models.CharField(max_length=30, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیحات')
    photo = models.ImageField(blank=True, null=True, verbose_name='عکس محصول')
    link_to_website = models.CharField(max_length=255, verbose_name='لینک محصول در وبسایت')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
