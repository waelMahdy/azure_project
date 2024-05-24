from django.db import models
from django.urls import reverse
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from rest_framework import serializers
from taggit.managers import TaggableManager
from django.db.models import Avg, Count
from accounts.models import Account
# Create your models here.

class Product(models.Model):
    category=models.ForeignKey('Category',on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug=models.SlugField(max_length=500,unique=True) 
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    old_price = models.DecimalField(max_digits=5, decimal_places=2,default=0,blank=True)
    image = models.ImageField(upload_to='photos/products', blank=True)
    image_1 = models.ImageField(upload_to='photos/products', blank=True)
    image_2 = models.ImageField(upload_to='photos/products', blank=True)
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(50, 60)],
                               format="JPEG",
                               options={'quality': 60})
    thumbnail_1 = ImageSpecField(source='image_1',
                                processors=[ResizeToFill(50, 60)],
                                format="JPEG",
                                options={'quality': 60})
    thumbnail_2 = ImageSpecField(source='image_2',
                                processors=[ResizeToFill(50, 60)],
                                format="JPEG",
                                options={'quality': 60})
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    is_new=models.BooleanField(default=False)
    on_sale=models.BooleanField(default=False)
    created_date=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)
    tags = TaggableManager()
    def __str__(self):
        return self.name
    def create_and_save_thumbnails(self):
        # Create and save thumbnails for the Category instance
        for image_field in ['image', 'image_1', 'image_2']:
            image = getattr(self, image_field)
            if image:
                thumbnail = ImageSpecField(source=image_field,
                                          processors=[ResizeToFill(50, 60)],
                                          format="JPEG",
                                          options={'quality': 60})
                setattr(self, f'thumbnail_{image_field}', thumbnail)
        self.save() 
    def average_review(self):
        reviews=ReviewRating.objects.filter(product=self,status=True).aggregate(average=Avg('rating')) 
        avg=0
        if reviews['average'] is not None:
            avg=float(reviews['average'])
        return avg    
    def count_reviews(self):
        reviews=ReviewRating.objects.filter(product=self,status=True).aggregate(average=Count('rating')) 
        count=0
        if reviews['average'] is not None:
            count=int(reviews['average'])
        return count    
    def get_url(self):
        return reverse('product',args=[self.id])

class Tag(models.Model):
    name= models.CharField(max_length=200,blank=True)
    

class Category(models.Model):
    name=models.CharField(max_length=100)
    slug=models.SlugField(max_length=500,unique=True) 
    description=models.TextField(max_length=1000,blank=True)  
    image=models.ImageField(upload_to='photos/categories',blank=True) 
    class Meta:
        verbose_name='category'
        verbose_name_plural='categories'
    def get_category_url(self):
        return reverse('shop_by_category',args=[self.slug])    
    def __str__(self):
        return self.name    

class ReviewRating(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,default='')
    user=models.ForeignKey(Account,on_delete=models.CASCADE,default='')
    subject=models.CharField(max_length=200,blank=True)
    review=models.TextField(max_length=500,blank=True)
    rating=models.FloatField()
    ip=models.CharField(max_length=39,blank=True)
    status=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)  
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active=True)   
variation_category_choice=(('color','color'),('size','size'))   
class Variation(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=100,choices=variation_category_choice)
    variation_value=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    objects=VariationManager()

    def __str__(self):
        return self.variation_value