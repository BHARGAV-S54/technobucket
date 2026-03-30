from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    features = models.JSONField(default=list)
    is_popular = models.BooleanField(default=False)
    is_combo = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name

    @property
    def savings(self):
        """Calculate savings based on original price, if available."""
        if self.original_price and self.original_price > self.price:
            return self.original_price - self.price
        return 0


class Testimonial(models.Model):
    customer_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    rating = models.IntegerField(default=5)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', 'sort_order']

    def __str__(self):
        return f"{self.customer_name} - {self.company}"


class ContactInquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('spam', 'Spam'),
    ]

    SUBMISSION_TYPE_CHOICES = [
        ('inquiry', 'Contact Inquiry'),
        ('ats_resume', 'ATS Resume Form'),
        ('combo_pack', 'Combo Pack Form'),
        ('custom_project', 'Custom Project Form'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    service_name = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPE_CHOICES, default='inquiry')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Contact Inquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.email}"
