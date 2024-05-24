from django.contrib import admin
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from store.models import Category, Product, ReviewRating, Variation

# Register your models here.
class productAdmin(admin.ModelAdmin):
    list_display = ('name','price', 'stock','image', 'thumbnail')
    search_fields = ['name']
    prepopulated_fields = {"slug": ("name",)}
    # def save_model(self, request, obj, form, change):
    #     # Create and save thumbnails for the Category instance
    #     obj.create_and_save_thumbnails()

    #     # Call the parent class's save_model method
    #     super().save_model(request, obj, form, change)
    def save_model(self, request, obj, form, change):
        # Create and save thumbnails for the Category instance
        obj.create_and_save_thumbnails()

        # Call the parent class's save_model method
        super().save_model(request, obj, form, change)
class VariationAdmin(admin.ModelAdmin):
    list_display=( 'product','variation_category','variation_value','is_active')
    list_editable=('is_active',)
    list_filter=( 'product','variation_category','variation_value','is_active')    

class categoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(Product,productAdmin)
admin.site.register(Category,categoryAdmin)
admin.site.register(ReviewRating)
admin.site.register(Variation,VariationAdmin)