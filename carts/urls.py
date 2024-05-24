from . import views
from django.urls import path, include



urlpatterns = [

    path('', views.cart,name='cart'),
    path('add_item/<int:product_id>', views.add_item,name='add_item'),
    path('add_item', views.add_item,name='add_item_html'),
    path('delete', views.delete_cart_item,name='delete_cart_item'),
    path('remove', views.remove_cart_item,name='remove_cart_item'),
    path('checkout', views.checkout,name='checkout'),
   
]
