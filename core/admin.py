from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Product, Order

class UserProfileAdmin(UserAdmin):
    # Add custom fields to user admin display
    list_display = ('username', 'email', 'role', 'raw_password_view', 'profile_image_preview', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('SCM Role Settings', {'fields': ('role', 'profile_picture', 'raw_password_view')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('SCM Role Settings', {'fields': ('role', 'profile_picture', 'raw_password_view')}),
    )
    
    def profile_image_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 50%; object-fit: cover;" />', obj.profile_picture.url)
        return "No Image"
    profile_image_preview.short_description = 'Profile Image'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'available_quantity', 'offer_percentage', 'discounted_price', 'image_preview')
    list_filter = ('vendor',)
    search_fields = ('name', 'description')
    
    def image_preview(self, obj):
        if obj.image1:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 4px; object-fit: cover;" />', obj.image1.url)
        return "No Image"
    image_preview.short_description = 'Image'

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'buyer', 'quantity', 'total_price', 'payment_method', 'status', 'otp', 'order_confirmed_at', 'delivered_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('product__name', 'buyer__username', 'otp')
    readonly_fields = ('otp', 'order_confirmed_at')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
