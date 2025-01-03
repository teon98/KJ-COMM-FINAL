from django.db import models
from django.conf import settings

# Create your models here.
class Blog(models.Model): #글게시판 모델
    title = models.CharField(max_length=100)
    # author = models.CharField(max_length=50)
    #head_image = models.ImageField(upload_to='shop/images/%y/%m/%d/', blank=True)
    #file_upload = models.FileField(upload_to='shop/Files/%y/%m/%d/', blank=True)
    content = models.TextField()
    #price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f'[{self.pk}] {self.title}'
    
    def get_absolute_url(self):
        return f'/shop/blog/{self.pk}/'

class Post(models.Model): #이미지 게시판 모델
    title = models.CharField(max_length=100)
    #author = models.CharField(max_length=50)
    head_image = models.ImageField(upload_to='shop/images/%y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='shop/Files/%y/%m/%d/', blank=True)
    content = models.TextField()
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f'[{self.pk}] {self.title}'
    
    def get_absolute_url(self):
        return f'/shop/post/{self.pk}'