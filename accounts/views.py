import json

import threading
from urllib.parse import urlparse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from accounts.form import RegisterationForm, UserForm, UserProfileForm
from accounts.models import Account, UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth 
#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct
from project import settings
class EmailThread(threading.Thread):
    def __init__(self,email_message):
        self.email_message=email_message
        threading.Thread.__init__(self)
    def run(self):
        self.email_message.send() 
# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        # cart=request.session.create
        request.session['cart'] = cart
    return cart 
def register(request):
    if request.method=='POST':
        form = RegisterationForm(data=request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split('@',1)[0]
            user=Account.objects.create_user(username=username,first_name=first_name,last_name= last_name,email=email,password=password) 
            user.phone_number =phone_number 
            user.save()
            #USER VERIFICATION
            current_site=get_current_site(request)
            mail_subject='Activate Your Account'
            message=render_to_string('accounts/account_verification_mail.html',{
                "user":user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                })
            
            email_message=EmailMessage(mail_subject,message,settings.EMAIL_HOST_USER, [email])
            email_message.content_subtype='html'
            EmailThread(email_message).start()
            if user:
                messages.success(request,f"Account created for {first_name}. We sent you an email please follow instructions to activate your account.")
                return redirect('login')
            else:
                return redirect('register')

   
    else:
        form=RegisterationForm()
    context={
        'form':form,
       }

    return render(request,'accounts/register.html',context)

def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
        token_generator=default_token_generator.check_token(user,token)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and token_generator :
        user.is_active=True
        user.save()
        messages.success(request,"Your Account is activated.")
        
        return redirect("login")

    else:
        messages.error(request,"The activation link is expired or used.")
       
        return redirect("register",)


def login(request):
    if request.method == "POST":
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(username=email,password=password)    
        if user is not None:           
            try: 
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exist= CartItem.objects.filter(cart=cart).exists() 
                if is_cart_item_exist:
                    cart_items=CartItem.objects.filter(cart=cart)
                    product_variations=[]
                    for item in cart_items:
                        variations=item.variations.all()
                        product_variations.append(list(variations))
                    #get the user items from the user to access its productc variations 
                    cart_items=CartItem.objects.filter(user=user)  
                    ex_va_list=[]
                    id=[]   
                    for item in cart_items:
                        exisiting_variation=item.variations.all()
                        ex_va_list.append(list(exisiting_variation))
                        id.append(item.id)  
                    for pr in product_variations:
                        if pr in ex_va_list:
                            index=ex_va_list.index(pr)
                            item_id=id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user=user
                            item.save()
                        else:
                            cart_items=CartItem.objects.filter(cart=cart)
                            for item in cart_items:
                                item.user=user
                                item.save()  
            except:
                pass                               
            if not user.is_active:
                messages.error(request,"Account is not activated yet.Activate it then try again.")
                return redirect('login')
            auth.login(request,user)
            messages.success(request,"You are now logged in.")
            url=request.META.get('HTTP_REFERER')
            try:
               #query=urlparse(url).query.split("=")[1]
               query=urlparse(url).query               
               params=dict(x.split('=') for x in query.split('&'))
               if 'next' in params:
                   next_page=params['next']
                   return redirect(next_page)                
            except:
               return redirect('dashboard')   
        else:
           
            messages.error(request,"Invalid Email or Password")
            return redirect('login')

            
    else:
        try:
            if request.user.is_authenticated and UserSocialAuth.objects.get(user_id=request.user.id):
                messages.success(request,'User logged in successfully by Google.')
        except:
            pass        
        return render(request,'accounts/login.html')    
@login_required(login_url='login') 
def logout(request):
    auth.logout(request)
    messages.info(request,"Logged out successfully")
    return redirect('login') 

def change_password(request):
    if request.method == 'POST':
        current_password=request.POST['current_password']
        new_password=request.POST['new_password']
        confirm_password=request.POST['confirm_new_password']
        user=Account.objects.get(username__exact=request.user.username)
        if new_password==confirm_password:
            success= user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.info(request,"Password Successfully Changed!")
                return redirect('login')
            else:
                messages.error(request,'Current Password is Incorrect')
                return redirect('change_password')
        else:
            messages.error(request,'New password and Confirm New Password do not match')
            return redirect('change_password')    

    return render(request, 'accounts/change_password.html') 

@login_required(login_url='login')  
def dashboard(request):
         
    if request.user.is_authenticated:
        try:
            try:
                userprofile=UserProfile.objects.get(user=request.user)
            except UserSocialAuth.DoesNotExist:
                userprofile=UserSocialAuth.objects.get(user_id=request.user.id)
            
            orders=Order.objects.order_by( '-created_at').filter(user=request.user,is_ordered=True)
            orders_count=orders.count() 
            
        except UserSocialAuth.DoesNotExist:
            userprofile=UserProfile.objects.get(user=request.user)
            orders=Order.objects.order_by( '-created_at').filter(user=request.user,is_ordered=True)
            orders_count=orders.count() 
        
         

    else:
        userprofile=None
        orders=None  
        orders_count=0 
    context={
        'userprofile':userprofile,
        'orders':orders,
        'orders_count':orders_count,
    }    
    return render(request,'accounts/dashboard.html',context)    

def my_orders(request):
    try:
      orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    except:
        orders=None  
    context={
        'orders':orders
    }
    return render(request,'accounts/my_orders.html',context)
def order_details(request,order_id):
    order=Order.objects.get(order_number=order_id)
    order_details=OrderProduct.objects.filter(order__order_number=order_id)
    sub_total=0
    
    for i in order_details:
        sub_total+=i.product.price*i.quantity
    grand_total=float(sub_total)+order.tax
    context={
        'order':order,
        'order_details':order_details,
        'sub_total':sub_total,
        'grand_total':grand_total
        }
    return render(request,'accounts/order_details.html',context)
def edit_profile(request):
    try:
        user_profile=UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
         user_profile=UserProfile.objects.create(user=request.user)
    if request.method == 'POST':
        user_form=UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"Profile updated Successfully")
            return redirect('dashboard')
    else:
        user_form=UserForm(instance=request.user)
        profile_form=UserProfileForm(instance=user_profile)
    context={
        'user_form':user_form,
        'profile_form':profile_form,
        'user_profile':user_profile
    }    
    return render(request,'accounts/edit_profile.html',context)  



