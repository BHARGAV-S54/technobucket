from django.contrib import admin
from .models import Service, Testimonial, ContactInquiry


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_popular', 'is_combo', 'is_active', 'sort_order']
    list_filter = ['is_active', 'is_popular', 'is_combo']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'role', 'company', 'is_featured', 'is_active']
    list_filter = ['is_featured', 'is_active']
    search_fields = ['customer_name', 'company', 'content']


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'service_name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['ip_address', 'created_at', 'updated_at']
