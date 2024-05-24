
import json
from django.core.serializers.json import DjangoJSONEncoder

from carts.models import Cart, CartItem
from store.models import Category
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        # cart=request.session.create
        request.session['cart'] = cart
    return cart  

def get_categories(request):
    categories=Category.objects.all()
    return  {'categories':categories}
def get_cart_count(request):
    items_count=0
    cart_items={}
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart=Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items=CartItem.objects.all().filter(user=request.user)
            else:
                cart_items=CartItem.objects.all().filter(cart=cart[:1])
            for item in cart_items:
                items_count+=item.quantity
        except Cart.DoesNotExist:
            items_count=0
        
    return {'cart_count':items_count}  
def get_cart_items(request):
  
    cart_items=None
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart=Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items=CartItem.objects.all().filter(user=request.user)
            else:
                cart_items=CartItem.objects.all().filter(cart=cart[:1])
        except Cart.DoesNotExist:
            cart_items=None
        
      
    return {'cart_items':cart_items}              