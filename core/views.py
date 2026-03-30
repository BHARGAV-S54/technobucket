from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, Testimonial, ContactInquiry
from django.utils.html import format_html
from django.http import HttpResponse
from .pdf_generator import generate_inquiry_pdf, generate_portfolio_order_pdf


def home(request):
    """Home page view"""
    services = list(Service.objects.filter(is_active=True, is_combo=False)[:4])
    testimonials = list(Testimonial.objects.filter(is_active=True, is_featured=True)[:3])

    # Provide a fallback set of demo content when the database is empty.
    if not services:
        services = [
            {
                'name': 'ATS Resume',
                'price': 40,
                'description': 'Beat the bots with a resume designed for Applicant Tracking Systems.',
                'is_popular': False,
            },
            {
                'name': 'Portfolio',
                'price': 299,
                'description': 'Showcase your work with a modern, professional portfolio.',
                'is_popular': True,
            },
            {
                'name': 'Custom Project',
                'price': 999,
                'description': 'Full development support to build a complete custom project.',
                'is_popular': False,
            },
            {
                'name': 'Profile Creation',
                'price': 149,
                'description': 'Optimize your LinkedIn and professional profiles for recruiters.',
                'is_popular': False,
            },
        ]

    if not testimonials:
        testimonials = [
            {
                'customer_name': 'Rahul Sharma',
                'role': 'Software Engineer',
                'company': 'Google',
                'content': 'Techno Bucket helped me create a stunning portfolio that got me noticed by top companies.',
            },
            {
                'customer_name': 'Priya Patel',
                'role': 'Product Manager',
                'company': 'Microsoft',
                'content': 'The ATS-friendly resume was a game changer. I started getting interview calls immediately!',
            },
            {
                'customer_name': 'Amit Kumar',
                'role': 'Data Scientist',
                'company': 'Amazon',
                'content': 'Best investment for my career. The combo pack gave me everything I needed.',
            },
        ]

    context = {
        'services': services,
        'testimonials': testimonials,
    }
    return render(request, 'core/home.html', context)


def services(request):
    """Services page view"""
    services = list(Service.objects.filter(is_active=True, is_combo=False))
    combo_pack = Service.objects.filter(is_active=True, is_combo=True).first()

    # Provide sensible demo content when DB has no entries yet
    if not combo_pack:
        combo_pack = {
            'name': 'Complete Career Combo Pack',
            'description': 'Get everything you need to launch your career! This exclusive combo includes all our premium services at a special discounted price.',
            'price': 1119,
            'original_price': 1487,
            'savings': 368,
            'features': [
                'ATS-Friendly Resume (₹40)',
                'Portfolio Website (₹299)',
                'Professional Profile Creation (₹149)',
                'FREE Custom Project Consultation (₹999 value)',
                'Priority Support',
                'Save ₹368 (25% off)',
            ],
        }

    if not services:
        services = [
            {
                'name': 'ATS-Friendly Resume',
                'slug': 'ats-resume',
                'price': 40,
                'description': 'Get past the bots and land interviews with our professionally crafted, ATS-optimized resumes that highlight your skills.',
                'features': [
                    'ATS-Optimized Format',
                    'Keyword Research',
                    'Multiple Revisions',
                    'PDF & Word Export',
                ],
                'is_popular': False,
            },
            {
                'name': 'Portfolio Website',
                'slug': 'portfolio-website',
                'price': 299,
                'description': 'Showcase your work with a stunning, responsive portfolio website that impresses recruiters and clients alike.',
                'features': [
                    'Responsive Design',
                    'Custom Domain Setup',
                    '5 Pages Included',
                    'Contact Form Integration',
                ],
                'is_popular': True,
            },
            {
                'name': 'Custom Project',
                'slug': 'custom-project',
                'price': 999,
                'description': 'Need something unique? We build custom web applications, tools, and solutions tailored to your exact requirements.',
                'features': [
                    'Full-Stack Development',
                    'Modern Tech Stack',
                    'Scalable Architecture',
                    '3 Months Support',
                ],
                'is_popular': False,
            },
            {
                'name': 'Professional Profile Creation',
                'slug': 'profile-creation',
                'price': 149,
                'description': 'Stand out on LinkedIn and other professional platforms with an optimized profile that attracts opportunities.',
                'features': [
                    'LinkedIn Optimization',
                    'Headline & Summary',
                    'Skills Endorsement Strategy',
                    'Profile Photo Tips',
                ],
                'is_popular': False,
            },
        ]

    context = {
        'services': services,
        'combo_pack': combo_pack,
    }
    return render(request, 'core/services.html', context)


def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        service_id = request.POST.get('service')
        message_text = request.POST.get('message')
        
        inquiry = ContactInquiry(
            name=name,
            email=email,
            message=message_text,
            ip_address=get_client_ip(request)
        )
        
        if service_id:
            try:
                service = Service.objects.get(id=service_id)
                inquiry.service = service
                inquiry.service_name = service.name
            except Service.DoesNotExist:
                pass
        
        inquiry.save()
        messages.success(request, 'Your message has been sent! We will get back to you soon.')
        return redirect('contact')
    
    services_list = Service.objects.filter(is_active=True)
    # Prefill support (used by Custom Project "Order" CTA)
    selected_service_id = request.GET.get('service', '') or ''
    prefill_message = request.GET.get('message', '') or ''
    context = {
        'services_list': services_list,
        'selected_service_id': selected_service_id,
        'prefill_message': prefill_message,
    }
    return render(request, 'core/contact.html', context)


def custom_project(request):
    """Custom Project selection page (2-pane UI)"""
    # Link the Order button to the Contact form.
    custom_service = Service.objects.filter(slug='custom-project', is_active=True).first()
    custom_service_id = custom_service.id if custom_service else ''

    projects = [
        {
            'id': 'saas',
            'name': 'SaaS Dashboard',
            'description': 'A scalable multi-tenant SaaS dashboard with authentication, billing-ready architecture, role-based access, and analytics.',
            'techstack': ['Django', 'React', 'PostgreSQL', 'JWT/SSO'],
        },
        {
            'id': 'ecommerce',
            'name': 'E-commerce Platform',
            'description': 'A fast, modern e-commerce platform with product management, cart/checkout flows, and performance-optimized UI.',
            'techstack': ['Django', 'Next.js', 'PostgreSQL', 'Stripe-ready design'],
        },
        {
            'id': 'automation',
            'name': 'Automation & Integrations',
            'description': 'Integrate tools and build workflows: webhooks, background jobs, dashboards, and secure integrations for teams.',
            'techstack': ['Python', 'Celery', 'PostgreSQL', 'REST/Webhooks'],
        },
        {
            'id': 'mobile',
            'name': 'Web App + Mobile-ready UI',
            'description': 'A responsive web app UI that is mobile-ready, with polished UX and maintainable component architecture.',
            'techstack': ['Django', 'React', 'TypeScript', 'REST API'],
        },
    ]

    # Add a prebuilt "order message" per project to send users to Contact.
    for p in projects:
        p['order_message'] = (
            f"Custom Project Request: {p['name']}\n\n"
            f"Description: {p['description']}\n\n"
            f"Tech stack: {', '.join(p['techstack'])}\n\n"
            f"Please contact me with next steps, timeline, and estimate."
        )

    context = {
        'projects': projects,
        'custom_service_id': custom_service_id,
    }
    return render(request, 'core/custom_project.html', context)


def ats_resume_form(request):
    """ATS-friendly resume intake form view"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Build a structured message from the submitted fields
        lines = []
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken' or not value:
                continue
            label = key.replace('_', ' ').title()
            lines.append(f"{label}: {value}")

        message_text = "ATS-Friendly Resume Form Submission\n\n" + "\n".join(lines)

        inquiry = ContactInquiry(
            name=full_name or 'Unknown',
            email=email or '',
            message=message_text,
            submission_type='ats_resume',
            ip_address=get_client_ip(request)
        )

        # Try to attach the ATS service if it exists
        ats_service = Service.objects.filter(slug='ats-resume').first()
        if ats_service:
            inquiry.service = ats_service
            inquiry.service_name = ats_service.name

        inquiry.save()
        messages.success(request, 'Your details have been submitted! We will contact you with your ATS-optimized resume plan.')
        return redirect('services')

    return render(request, 'core/ats_resume_form.html')


def combo_pack_form(request):
    """Combo Pack intake form (covers resume + portfolio + profile needs)"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Build a structured message from submitted fields
        lines = []
        for key, value in request.POST.items():
            if key == 'csrfmiddlewaretoken' or not value:
                continue
            label = key.replace('_', ' ').title()
            lines.append(f"{label}: {value}")

        message_text = "Combo Pack Form Submission\n\n" + "\n".join(lines)

        inquiry = ContactInquiry(
            name=full_name or 'Unknown',
            email=email or '',
            message=message_text,
            submission_type='combo_pack',
            ip_address=get_client_ip(request)
        )

        combo_service = Service.objects.filter(is_active=True, is_combo=True).first()
        if combo_service:
            inquiry.service = combo_service
            inquiry.service_name = combo_service.name

        inquiry.save()
        messages.success(request, 'Thanks! Your combo pack request is in. Proceed to payment to confirm your order.')
        return redirect('payment')

    return render(request, 'core/combo_pack_form.html')


def payment_page(request):
    """Simple payment handoff page"""
    combo_service = Service.objects.filter(is_active=True, is_combo=True).first()
    return render(request, 'core/payment.html', {'combo_service': combo_service})


def admin_login(request):
    """Admin login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Hardcoded credentials as requested
        if username == 'technobucket' and password == 'bhargav':
            # Create or get admin user
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(username='admin')
            except User.DoesNotExist:
                user = User.objects.create_superuser('admin', 'admin@technobucket.com', password)
            
            user = authenticate(request, username='admin', password=password)
            if user is None:
                # Set password if not set
                user = User.objects.get(username='admin')
                user.set_password(password)
                user.save()
                user = authenticate(request, username='admin', password=password)
            
            if user:
                login(request, user)
                return redirect('admin_dashboard')
        
        messages.error(request, 'Invalid credentials')
    
    return render(request, 'core/admin_login.html')


@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    from orders.models import PortfolioOrder
    
    # Get portfolio orders
    portfolio_orders = PortfolioOrder.objects.all().order_by('-created_at')
    
    # Get service form submissions (from ContactInquiry)
    service_submissions = ContactInquiry.objects.filter(
        submission_type__in=['ats_resume', 'combo_pack']
    ).order_by('-created_at')
    
    # Get actual contact inquiries (messages) - exclude service form submissions
    inquiries = ContactInquiry.objects.filter(
        submission_type='inquiry'
    ).order_by('-created_at')
    
    # Combine portfolio orders with service submissions for the orders section
    all_orders = list(portfolio_orders) + list(service_submissions)
    all_orders.sort(key=lambda x: x.created_at, reverse=True)
    
    context = {
        'orders': portfolio_orders,
        'service_submissions': service_submissions,
        'inquiries': inquiries,
        'new_inquiries': inquiries.filter(status='new').count(),
        'total_orders': portfolio_orders.count() + service_submissions.count(),
        'pending_orders': portfolio_orders.filter(status='pending').count(),
        'completed_orders': portfolio_orders.filter(status='completed').count(),
    }
    return render(request, 'core/admin_dashboard.html', context)


def admin_logout_view(request):
    """Admin logout view"""
    logout(request)
    return redirect('home')


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def download_inquiry_pdf(request, inquiry_id):
    """Download PDF for a contact inquiry"""
    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    pdf_buffer = generate_inquiry_pdf(inquiry)

    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="inquiry_{inquiry.id}_{inquiry.name.replace(" ", "_")}.pdf"'
    return response


@login_required
def download_order_pdf(request, order_id):
    """Download PDF for a portfolio order"""
    from orders.models import PortfolioOrder
    order = get_object_or_404(PortfolioOrder, id=order_id)
    pdf_buffer = generate_portfolio_order_pdf(order)

    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id:05d}_{order.full_name.replace(" ", "_")}.pdf"'
    return response
