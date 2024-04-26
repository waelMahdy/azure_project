from django.contrib import admin

from store.models import Category, Product

# Register your models here.
class productAdmin(admin.ModelAdmin):
    list_display = ('name','price', 'stock')
    search_fields = ['name']
    prepopulated_fields = {"slug": ("name",)}
class categoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(Product,productAdmin)
admin.site.register(Category,categoryAdmin)
