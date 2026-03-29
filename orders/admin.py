from django.contrib import admin
from .models import PortfolioOrder, PortfolioFile, OrderNote


class PortfolioFileInline(admin.TabularInline):
    model = PortfolioFile
    extra = 0
    readonly_fields = ['uploaded_at']


class OrderNoteInline(admin.StackedInline):
    model = OrderNote
    extra = 1


@admin.register(PortfolioOrder)
class PortfolioOrderAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['full_name', 'email', 'github_profile', 'linkedin_profile']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    inlines = [PortfolioFileInline, OrderNoteInline]
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Profile Links', {
            'fields': ('github_profile', 'leetcode_profile', 'linkedin_profile')
        }),
        ('Skills & Projects', {
            'fields': ('skills', 'project_links')
        }),
        ('Extra Information', {
            'fields': ('extra_information',)
        }),
        ('Order Status', {
            'fields': ('status', 'payment_status', 'amount_paid')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PortfolioFile)
class PortfolioFileAdmin(admin.ModelAdmin):
    list_display = ['order', 'file_type', 'original_filename', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
