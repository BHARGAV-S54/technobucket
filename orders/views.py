from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from core.models import Service
from .models import PortfolioOrder, PortfolioFile
import json


def portfolio_order(request):
    """Portfolio order form view"""
    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        github_profile = request.POST.get('github_profile', '')
        leetcode_profile = request.POST.get('leetcode_profile', '')
        linkedin_profile = request.POST.get('linkedin_profile', '')
        skills = request.POST.get('skills')
        extra_information = request.POST.get('extra_information', '')
        
        # Process project links
        project_links = []
        for key in request.POST:
            if key.startswith('project_link_'):
                value = request.POST.get(key)
                if value:
                    project_links.append(value)
        
        # Process skills into list
        skills_list = [s.strip() for s in skills.split(',') if s.strip()]
        
        # Create order
        order = PortfolioOrder.objects.create(
            full_name=full_name,
            email=email,
            github_profile=github_profile or '',
            leetcode_profile=leetcode_profile or '',
            linkedin_profile=linkedin_profile or '',
            skills=skills_list,
            project_links=project_links,
            extra_information=extra_information,
            status='pending',
            payment_status='pending'
        )
        
        # Handle file uploads
        # Resume
        if 'resume' in request.FILES:
            resume = request.FILES['resume']
            PortfolioFile.objects.create(
                order=order,
                file_type='resume',
                original_filename=resume.name,
                stored_filename=f"resume_{order.id}_{resume.name}",
                file=resume,
                file_size=resume.size,
                mime_type=resume.content_type
            )
        
        # Profile Image
        if 'profile_image' in request.FILES:
            profile_image = request.FILES['profile_image']
            PortfolioFile.objects.create(
                order=order,
                file_type='profile_image',
                original_filename=profile_image.name,
                stored_filename=f"profile_{order.id}_{profile_image.name}",
                file=profile_image,
                file_size=profile_image.size,
                mime_type=profile_image.content_type
            )
        
        # Certificates
        for key in request.FILES:
            if key.startswith('certificate_'):
                cert = request.FILES[key]
                PortfolioFile.objects.create(
                    order=order,
                    file_type='certificate',
                    original_filename=cert.name,
                    stored_filename=f"cert_{order.id}_{cert.name}",
                    file=cert,
                    file_size=cert.size,
                    mime_type=cert.content_type
                )
        
        # Align payable amount with the service price if available
        portfolio_service = Service.objects.filter(slug='portfolio-website', is_active=True).first()
        if portfolio_service:
            order.amount_paid = portfolio_service.price
            order.save(update_fields=['amount_paid'])

        messages.success(request, 'Your order has been submitted! Complete payment to confirm your portfolio build.')

        payment_url = reverse('payment')
        if portfolio_service:
            payment_url = f"{payment_url}?service_slug={portfolio_service.slug}&order_type=portfolio&record_id={order.id}"
        return redirect(payment_url)
    
    return render(request, 'orders/portfolio_order.html')


def update_order_status(request, order_id):
    """Update order status via AJAX"""
    if request.method == 'POST' and request.user.is_authenticated:
        order = get_object_or_404(PortfolioOrder, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(PortfolioOrder.STATUS_CHOICES):
            order.status = new_status
            if new_status == 'completed':
                from django.utils import timezone
                order.completed_at = timezone.now()
            order.save()
            return JsonResponse({'success': True, 'status': new_status})
    
    return JsonResponse({'success': False}, status=400)
