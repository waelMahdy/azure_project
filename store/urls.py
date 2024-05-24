"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.urls import path, include


urlpatterns = [

    path('', views.shop,name='shop'),
    path('category/<slug:category_slug>', views.shop,name='shop_by_category'),
    path('sort_by/', views.sort_by,name='sort_by'),


    path('product/<int:product_id>', views.product,name='product'),
    path('search', views.search,name='search'),
    path('submit_review/<int:pk>', views.submit_review,name='submit_review'),
]
