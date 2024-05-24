from . import views
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('register/', views.register,name='register'),
    path('login/', views.login,name='login'),
    path('activate/<uidb64>/<token>', views.activate,name='activate'),
    path('logout/',views.logout,name='logout'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('change_password/',views.change_password,name='change_password'),
    path('',views.dashboard,name='dashboard'),
    path('my_orders/',views.my_orders,name='my_orders'),
    path('order_details/<int:order_id>',views.order_details,name='order_details'),
    path('social-auth/', include('social_django.urls', namespace='social')),

]
