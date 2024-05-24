from . import views
from django.urls import path, include



urlpatterns = [

    path('place_order', views.place_order,name='place_order'),
    path('payments',views.payments,name="payments"),
    path('order_complete/',views.order_complete,name="order_complete"),
   
]
