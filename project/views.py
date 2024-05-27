

from django.shortcuts import render

from store.models import Category, Product

def home(request):
    try:
        products=Product.objects.filter(is_available=True).all().order_by('-created_date')[:8]
        new_products=Product.objects.filter(is_available=True,is_new=True).all().order_by('-created_date')[:4]
        kids=Category.objects.get(name='Kids')
        men=Category.objects.get(name='Men')
        accessories=Category.objects.get(name="Accessories")
        women=Category.objects.get(name="Women")
    except:
        products=None
        new_products=None
        kids=None
        men=None
        accessories=None
        women=None

    
    context= {
        'products':products,
        'accessories':accessories,
        'kids':kids,
        'men':men,
        'women':women,
        'new_products':new_products
        }

    return render(request,'home/home.html',context)

def contact(request):
    return render(request,'home/contact.html')

def comming_soon(request):
    return render(request,'home/comming_soon.html')