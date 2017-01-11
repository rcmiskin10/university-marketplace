from django.contrib import admin

from .models import Product, Category, ServiceType, WantServiceType, DoService, WantService

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    class Meta:
        model = Product
    search_fields = ('owner__email',)
admin.site.register(Product, ProductAdmin)

class CategoryAdmin(admin.ModelAdmin):
    
    class Meta:
        model = Category
        
admin.site.register(Category, CategoryAdmin)


class WantServiceTypeAdmin(admin.ModelAdmin):
    
    class Meta:
        model = WantServiceType
        
admin.site.register(WantServiceType, WantServiceTypeAdmin)

class ServiceTypeAdmin(admin.ModelAdmin):
    
    class Meta:
        model = ServiceType
        
admin.site.register(ServiceType, ServiceTypeAdmin)

class DoServiceAdmin(admin.ModelAdmin):
    
    class Meta:
        model = DoService
        
admin.site.register(DoService, DoServiceAdmin)

class WantServiceAdmin(admin.ModelAdmin):
    
    class Meta:
        model = WantService
        
admin.site.register(WantService, WantServiceAdmin)