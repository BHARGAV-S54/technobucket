from django.db import models


class PortfolioOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Profile Links (all mandatory)
    github_profile = models.URLField(max_length=500)
    leetcode_profile = models.URLField(max_length=500)
    linkedin_profile = models.URLField(max_length=500)
    
    # Skills and Projects
    skills = models.JSONField(default=list)
    project_links = models.JSONField(default=list)
    
    # Extra Information
    extra_information = models.TextField(blank=True)
    
    # Order Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=1999.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Portfolio Order'
        verbose_name_plural = 'Portfolio Orders'

    def __str__(self):
        return f"{self.full_name} - {self.email}"


class PortfolioFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('resume', 'Resume'),
        ('profile_image', 'Profile Image'),
        ('certificate', 'Certificate'),
    ]

    order = models.ForeignKey(PortfolioOrder, on_delete=models.CASCADE, related_name='files')
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    original_filename = models.CharField(max_length=255)
    stored_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='orders/%Y/%m/')
    file_size = models.BigIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    sort_order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'uploaded_at']

    def __str__(self):
        return f"{self.file_type} - {self.original_filename}"


class OrderNote(models.Model):
    order = models.ForeignKey(PortfolioOrder, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    is_internal = models.BooleanField(default=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on {self.order.full_name}'s order"
