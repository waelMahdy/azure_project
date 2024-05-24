from django.contrib import messages,auth
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from accounts.models import Account, UserProfile
from store.forms import ReviewForm
from store.models import Category, Product, ReviewRating, Tag, Variation
from django.db.models import Q,Avg
from django.contrib.auth.decorators import  login_required
# Create your views here.

def shop(request,category_slug=None,tag=None):
   item_per_page=3
   products=None
   paged_products=None
   page=0
   if category_slug:
       category=get_object_or_404(Category,slug=category_slug)
       products=Product.objects.all().filter(category=category,is_available=True).order_by('-created_date')
       
   elif request.GET.get('tag'):
       tag=request.GET.get('tag')
       products=Product.objects.all().filter(tags__name__contains=tag) 
   elif  request.GET.get('size'):
       size=request.GET.get('size')
       products=Product.objects.all().filter(variation__variation_value=size).order_by('-created_date')   
   elif request.GET.get('color'):
       color=request.GET.get('color')
       products=Product.objects.all().filter(variation__variation_value=color).order_by('-created_date')  
   else:          
        products=Product.objects.all().order_by('-created_date')
   paginator=Paginator(products,3)
   page=request.GET.get('page')
   paged_products=paginator.get_page(page)
   paged=int(page) if page!=None else 1
   tags=[]
   colors={}
   sizes={}
   
   for product in products:
      if not product.tags.all() in tags:
         for i in product.tags.all():
            if i.name not in tags:
               tags.append(i.name)
      variations=Variation.objects.filter(product=product)
      for variation in variations:
         if variation.variation_category =='color' and  variation.variation_value not in colors:
            colored_prod=Variation.objects.filter(variation_value=variation.variation_value).count()
            colors[variation.variation_value]=colored_prod  
         if variation.variation_category =='size' and  variation.variation_value not in sizes:  
            sizes[variation.variation_value]=Variation.objects.filter(variation_value=variation.variation_value).count() 
   
   
                    
   context={
       'products':paged_products,
       'start_count': paged_products.object_list.count()+(paged-1)*item_per_page ,
       'paged_products':products.count(),
       'products_count':Product.objects.all().count(),
       'tags':tags,
       'colors':colors,
       'sizes':sizes,
    }
   return render (request, 'shop/shop.html',context)

def sort_by(request):
    item_per_page=3
    products=None
    paged_products=None
    page=0
   # Get the GET parameters
    sort = request.COOKIES.get('sort')
    products=Product.objects.all().order_by('-created_date')
    if not sort:
       return render (request, 'shop/shop.html',{'products':products})
    
    if 'new' in sort:
       products=products.filter(is_new=True).order_by('-created_date')
    elif 'low_to_high' in sort:
       products=products.order_by('price')
    elif 'rating' in sort:
       products=Product.objects.annotate(average_rating=Avg('reviewrating__rating')).order_by('-average_rating')
    elif 'high_to_low' in sort:
       products=products.order_by('-price') 
    else:
       products=products  
    paginator=Paginator(products,3)
    page=request.GET.get('page')
    paged_products=paginator.get_page(page)
    paged=int(page) if page!=None else 1  
    context={
       "products":paged_products,
       'start_count': paged_products.object_list.count()+(paged-1)*item_per_page ,
       'paged_products':products.count(),
       'products_count':  Product.objects.all().count(),
    }
    return render (request, 'shop/shop.html',context)

def product(request,product_id):
    product=Product.objects.get(id=product_id)
    try:
       related_product=Product.objects.order_by('created_date').filter(Q(name__icontains=product.name )| Q(description__icontains=product.description) | Q(category=product.category))[:4]
    except:
      related_product=Product.objects.order_by('created_date').all()[:4]
    reviews=ReviewRating.objects.filter(product=product)  
    for review in reviews:
       try:
        profile=UserProfile.objects.get(user=review.user)
        review.profile_image=profile.profile_picture.url
       except:
          review.profile_image=None
           
    context ={
        "product":product,
        "related_products":related_product,
        'reviews':reviews,
    }
    return render(request,'shop/product.html',context)
def search(request):
    result=None
    if 'keyword' in  request.GET:
      keyword=request.GET['keyword']
      if  keyword :
         result=Product.objects.order_by('created_date').filter(Q(name__icontains=keyword )| Q(description__icontains=keyword))
    count=result.count()
    context={
        'products':result,
        'count':count,
        'keyword':keyword,
    }
    return render(request,'shop/shop.html',context)

@login_required(login_url='login')
def submit_review(request,pk):
   url=request.META.get('HTTP_REFERER')
   user=Account.objects.get(id=request.user.id)
   product=Product.objects.get(id=pk)
   if request.method == 'POST':
        subject=request.POST['subject']
        rating=request.POST['rating']
        review=request.POST['review']
        checked = request.POST.getlist('check-notify')
        if 'on' in checked:
            user.notify_me=True
            user.save()
        try:
            previous_review=ReviewRating.objects.get(user__id=request.user.id,product=product)
            form=ReviewForm(request.POST,instance=previous_review)
            form.save()
            messages.success(request,'Thank you, your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            new_review=ReviewRating()
            new_review.subject=subject
            new_review.rating=rating
            new_review.review=review
            new_review.ip=request.META.get('REMOTE_ADDR')
            new_review.user=request.user
            new_review.product=product
            new_review.save()
            messages.success(request,'Thank you, your review has been submitted.')
            return redirect(url) 
   else:
      raise ValueError("Bad Request")