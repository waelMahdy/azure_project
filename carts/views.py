
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import  login_required
from carts.models import Cart, CartItem
from project.context_processors import get_cart_count
from store.models import Product, Variation


# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        # cart=request.session.create
        request.session['cart'] = cart
    return cart    

def cart(request,total=0,quantity=0,cart_items=None):
    tax=0
    grand_total=0
    try:
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True).all()
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True).all()
        for item in cart_items:
            total+=item.product.price*item.quantity
            quantity+=item.quantity  
        tax=(2*total)/100
        grand_total=tax+total    
    except ObjectDoesNotExist:
        pass
    context={
        'total':total,
        'quantity':quantity,
        'grand_total':grand_total,
        'cart_items':cart_items,
        'tax':tax,

    }

    return render(request,'cart/cart.html',context)
def add_item(request,product_id=None):
    current_user=request.user
    quantity_sent=0
    product_sent=None
    product_variations=[]
    quantity_sent=1
    
    if request.method=='POST':
            product_id=request.POST.get('id')
            if product_id:
              product_sent=Product.objects.get(id=product_id)
            
            product_sent=Product.objects.get(id=product_id) 
            try:
              quantity_sent= int(request.POST.get('quantity-number'))             
            except:
                pass  
            for item in request.POST:
                key=item
                value=request.POST[key]
                print(key,value)
                try:
                    variation=Variation.objects.get(product=product_sent,variation_category__iexact=key,variation_value__iexact=value)
                    product_variations.append(variation)
                except:
                    pass    
    if request.method=='GET':
        item_id=int(request.GET.get('id'))
        if item_id:
            cart_item=CartItem.objects.get(id=item_id)
            cart_item.quantity+=1
            cart_item.save()
            counter=get_cart_count(request)
            return JsonResponse({'success':True,'counter':counter})            

    if current_user.is_authenticated:   # user is logged in
        if product_id:
           product_sent=Product.objects.get(id=product_id)

        is_cart_item_exist=CartItem.objects.filter(user=current_user,product=product_sent).exists()
        if is_cart_item_exist:
            cart_items=CartItem.objects.filter(user=current_user,product=product_sent)
            ex_var_list=[]
            id=[]
            for i in cart_items:
                existing_variations=i.variations.all()
                ex_var_list.append(list(existing_variations))
                id.append(i.id)
            if product_variations in ex_var_list:
                index=ex_var_list.index(product_variations)
                #item.id=id[index]
                item=CartItem.objects.get(product=product_sent,id=id[index])
                item.quantity+=quantity_sent
                item.save() 
            else:
                item=CartItem.objects.create(user=current_user,product=product_sent,quantity=quantity_sent)
                if len(product_variations) >0:
                  item.variations.clear()
                  item.variations.add(*product_variations)  
                                               
                  item.save()
    
        else:
            cart_item=CartItem.objects.create(user=current_user,product=product_sent,quantity=quantity_sent)
            if len(product_variations) >0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)
            cart_item.save()
    else:
        if product_id:
          product_sent=Product.objects.get(id=product_id)
        try:
            variation=Variation.objects.get(product=product_sent,variation_category__iexact=key,variation_value__iexact=value)
            product_variations.append(variation)
        except: 
            pass  
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request)) #get  the cart of this user present in the session
        except Cart.DoesNotExist:
            cart=Cart.objects.create(cart_id=_cart_id(request))   #if there is no cart for this user then create a
            cart.save()
        is_cart_item_exist= CartItem.objects.filter(cart=cart,product=product_sent).exists()   
        if is_cart_item_exist:
            cart_items=CartItem.objects.filter(cart=cart,product=product_sent)   #get the item with this product and cart
            ex_var_list=[]
            id=[]
            for item in cart_items:
                existing_variations=item.variations.all()
                ex_var_list.append(list(existing_variations))
                id.append(item.id) 
            if product_variations in ex_var_list:  #increase the cart item quantity +1
                index=ex_var_list.index(product_variations)
                item.id=id[index]
                item=CartItem.objects.get(product=product_sent,id=item.id)
                item.quantity+=quantity_sent
                item.save() 
            else:
                item=CartItem.objects.create(cart=cart,product=product_sent,quantity=quantity_sent)
                if len(product_variations) >0:
                  item.variations.clear()
                  item.variations.add(*product_variations)                                
                  item.save()       

            
        else:
            cart_item=CartItem.objects.create(cart=cart,product=product_sent,quantity=quantity_sent)
            if len(product_variations) >0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)
            cart_item.save() 

    counter=get_cart_count(request)          
    return   JsonResponse({'success':True,'counter':counter})     

def delete_cart_item(request):
    try:
        item_id=0
        if request.method=='GET':
            item_id=int(request.GET.get('id'))
            if item_id:
                cart_item=CartItem.objects.get(id=item_id)
                if cart_item.quantity >1:
                    cart_item.quantity-=1
                    cart_item.save()
                    counter=get_cart_count(request) 
                    return  JsonResponse({'success':True,'counter':counter}) 
                else:
                    cart_item.delete()
                    counter=get_cart_count(request)     
                    return  JsonResponse({'success':True,'deleted':True,'counter':counter}) 
            else:
                counter=get_cart_count(request) 
                return JsonResponse({'success':False,'counter':counter}) 
    except Exception as e:
        print(e) 
        counter=get_cart_count(request)         
        return JsonResponse({'success':False,'counter':counter}) 

def remove_cart_item(request):
    if request.method=='GET':
        try:
            item_id=int(request.GET.get('id'))
            cart_item=CartItem.objects.get(id=item_id)
            cart_item.delete()
            counter=get_cart_count(request)
            return  JsonResponse({'success':True,'counter':counter})
        except Exception as e:
            print(e)
            return  JsonResponse({'success':False,'counter':counter})

@login_required(login_url='login')        
def checkout(request,total=0,quantity=0,cart_items=None):
    if  request.method=='POST':
        return HttpResponse('Ok')
    tax=0
    grand_total=0
    try:
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True).all()
        else:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True).all()
        for item in cart_items:
            total+=item.product.price*item.quantity
            quantity+=item.quantity
        tax=(2*total)/100
        grand_total=tax+total 

    except ObjectDoesNotExist:
        pass
  
        
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request,"cart/checkout.html",context)        