

from django.shortcuts import render

from store.models import Product


def home(request):
    products=Product.objects.filter(is_available=True).all().order_by('-created_date')
    for i in products:
        print(i.image)
    context= {
        'products':products
        }
    return render(request,'home/home.html',context)