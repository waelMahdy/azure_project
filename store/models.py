from django.db import models

# Create your models here.

class Product(models.Model):
    category=models.ForeignKey('Category',on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug=models.SlugField(max_length=500,unique=True) 

    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='photos/products', blank=True)
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    name=models.CharField(max_length=100)
    slug=models.SlugField(max_length=500,unique=True) 
    description=models.TextField(max_length=1000,blank=True)  
    image=models.ImageField(upload_to='photos/categories',blank=True) 
    class Meta:
        verbose_name='category'
        verbose_name_plural='categories'
    def __str__(self):
        return self.name    


