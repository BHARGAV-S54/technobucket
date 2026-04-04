from django.shortcuts import render, redirect, get_object_or_404
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, ContactInquiry
from django.utils.html import format_html
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from decimal import Decimal
from django.core.mail import EmailMessage
import base64
import json
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db import OperationalError
from django.db.models import Count, Q
from .pdf_generator import (
    generate_inquiry_pdf,
    generate_portfolio_order_pdf,
    generate_payment_invoice,
)


def home(request):
    """Home page view"""
    services = []

    try:
        services = list(Service.objects.filter(is_active=True, is_combo=False)[:4])
    except OperationalError:
        # Database not ready (e.g., migrations not applied in deployment). Use in-memory fallback content.
        services = []

    # Provide a fallback set of demo content when the database is empty.
    if not services:
        services = [
            {
                "name": "ATS Resume",
                "price": 99,
                "description": "Beat the bots with a resume designed for Applicant Tracking Systems.",
                "is_popular": False,
            },
            {
                "name": "Portfolio",
                "price": 1999,
                "description": "Showcase your work with a modern, professional portfolio.",
                "is_popular": True,
            },
            {
                "name": "Custom Project",
                "price": 4999,
                "description": "Full development support to build a complete custom project.",
                "is_popular": False,
            },
            {
                "name": "Profile Creation",
                "price": 999,
                "description": "Optimize your LinkedIn and professional profiles for recruiters.",
                "is_popular": False,
            },
        ]


    context = {
        "services": services,
    }
    return render(request, "core/home.html", context)


def services(request):
    """Services page view"""
    services = []
    combo_pack = None

    try:
        services = list(Service.objects.filter(is_active=True, is_combo=False))
        combo_pack = Service.objects.filter(is_active=True, is_combo=True).first()
    except OperationalError:
        services = []
        combo_pack = None

    # Provide sensible demo content when DB has no entries yet
    if not combo_pack:
        combo_pack = {
            "name": "Complete Career Combo Pack",
            "description": "Get everything you need to launch your career! This exclusive combo includes all our premium services at a special discounted price.",
            "price": 7999,
            "original_price": 8096,
            "savings": 97,
            "features": [
                "ATS-Friendly Resume (₹99)",
                "Portfolio Website (₹1999)",
                "Professional Profile Creation (₹999)",
                "FREE Custom Project Consultation (₹4999 value)",
                "Priority Support",
                "Save ₹97 (Combo Deal)",
            ],
        }

    if not services:
        services = [
            {
                "name": "ATS-Friendly Resume",
                "slug": "ats-resume",
                "price": 99,
                "description": "Get past the bots and land interviews with our professionally crafted, ATS-optimized resumes that highlight your skills.",
                "features": [
                    "ATS-Optimized Format",
                    "Keyword Research",
                    "Multiple Revisions",
                    "PDF & Word Export",
                ],
                "is_popular": False,
            },
            {
                "name": "Portfolio Website",
                "slug": "portfolio-website",
                "price": 1999,
                "description": "Showcase your work with a stunning, responsive portfolio website that impresses recruiters and clients alike.",
                "features": [
                    "Responsive Design",
                    "Custom Domain Setup",
                    "5 Pages Included",
                    "Contact Form Integration",
                ],
                "is_popular": True,
            },
            {
                "name": "Custom Project",
                "slug": "custom-project",
                "price": 4999,
                "description": "Need something unique? We build custom web applications, tools, and solutions tailored to your exact requirements.",
                "features": [
                    "Full-Stack Development",
                    "Modern Tech Stack",
                    "Scalable Architecture",
                    "3 Months Support",
                ],
                "is_popular": False,
            },
            {
                "name": "Professional Profile Creation",
                "slug": "profile-creation",
                "price": 999,
                "description": "Stand out on LinkedIn and other professional platforms with an optimized profile that attracts opportunities.",
                "features": [
                    "LinkedIn Optimization",
                    "Headline & Summary",
                    "Skills Endorsement Strategy",
                    "Profile Photo Tips",
                ],
                "is_popular": False,
            },
        ]

    context = {
        "services": services,
        "combo_pack": combo_pack,
    }
    return render(request, "core/services.html", context)


def contact(request):
    """Contact page view"""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        service_id = request.POST.get("service")
        message_text = request.POST.get("message")

        inquiry = ContactInquiry(
            name=name,
            email=email,
            message=message_text,
            ip_address=get_client_ip(request),
        )

        service = None
        if service_id:
            try:
                service = Service.objects.get(id=service_id)
                inquiry.service = service
                inquiry.service_name = service.name
            except Service.DoesNotExist:
                pass

        inquiry.save()
        messages.success(
            request, "Your message has been sent! We will get back to you soon."
        )

        # If a specific service was selected, send user to payment for that service
        if service:
            payment_url = (
                reverse("payment")
                + f"?service_slug={service.slug}&order_type=inquiry&record_id={inquiry.id}"
            )
            return redirect(payment_url)

        return redirect("contact")

    try:
        services_list = list(Service.objects.filter(is_active=True))
    except (OperationalError, Exception):
        services_list = []

    # Provide fallback demo services if database is empty
    if not services_list:
        services_list = [
            {"id": 1, "name": "ATS-Friendly Resume", "price": 99},
            {"id": 2, "name": "Portfolio Website", "price": 1999},
            {"id": 3, "name": "Custom Project", "price": 4999},
            {"id": 4, "name": "Professional Profile Creation", "price": 999},
        ]

    # Prefill support (used by Custom Project "Order" CTA)
    selected_service_id = request.GET.get("service", "") or ""
    prefill_message = request.GET.get("message", "") or ""
    context = {
        "services_list": services_list,
        "selected_service_id": selected_service_id,
        "prefill_message": prefill_message,
    }
    return render(request, "core/contact.html", context)


def custom_project(request):
    """Custom Project selection page (2-pane UI)"""
    # Link the Order button to the Contact form.
    try:
        custom_service = Service.objects.filter(slug="custom-project", is_active=True).first()
        custom_service_id = custom_service.id if custom_service else 3  # Fallback to ID 3 from demo services
    except (OperationalError, Exception):
        custom_service_id = 3

    projects = [
        {
            "id": "travelguide",
            "name": "TravelGuide AI",
            "description": "An intelligent travel AI that plans the travel plans—crafting personalized itineraries, suggesting destinations, and optimizing every step of your journey.",
            "techstack": ["Python", "Next.js", "OpenAI API", "Google Maps"],
            "demo_url": "https://explore-with-ai-custom-itinera-git-5dddbf-bhargav-s54s-projects.vercel.app/",
            "image_url": "images/projects/travelguide.png",
        },
        {
            "id": "fakedetector",
            "name": "Risk Analyzer - Phishing Detection",
            "description": "Real-time AI analysis engine that scans URLs for phishing risks by analyzing SSL status, behavioral patterns, and cross-referencing known threat databases.",
            "techstack": ["Python", "AI/ML Heuristics", "React", "Cyber-security API"],
            "demo_url": "https://hack-five-self.vercel.app/",
            "image_url": "images/projects/fakedetector.png",
        },
        {
            "id": "codebattle",
            "name": "CODE Battle - Proctoring & AI Evaluation",
            "description": "Overview\n\nCODE Battle is a high-stakes competitive programming platform designed for secure, real-time assessments. It features advanced proctoring capabilities like live tab-tracking and environment locking, combined with Gemini-powered automated code evaluation for fair and accurate performance analysis.\n\nKey Features:\n• Real-time Proctoring & Tab Monitoring\n• AI-Powered Solution Evaluation (Gemini)\n• Scalable Multi-player Coding Environment\n• Production-ready for Render & Heroku",
            "techstack": ["Node.js", "Socket.io", "PostgreSQL", "Gemini AI", "Express"],
            "demo_url": "https://codebattle-tau.vercel.app/",
            "image_url": "images/projects/codebattle.png",
            "is_blueprint": True,
        },
        {
            "id": "mobile",
            "name": "Web App + Mobile-ready UI",
            "description": "A responsive web app UI that is mobile-ready, with polished UX and maintainable component architecture.",
            "techstack": ["Django", "React", "TypeScript", "REST API"],
        },
    ]

    # Add a prebuilt "order message" per project to send users to Contact.
    for p in projects:
        p["order_message"] = (
            f"Custom Project Request: {p['name']}\n\n"
            f"Description: {p['description']}\n\n"
            f"Tech stack: {', '.join(p['techstack'])}\n\n"
            f"Please contact me with next steps, timeline, and estimate."
        )

    context = {
        "projects": projects,
        "custom_service_id": custom_service_id,
    }
    return render(request, "core/custom_project.html", context)


def ats_resume_form(request):
    """ATS-friendly resume intake form view"""
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        # Build a structured message from the submitted fields
        lines = []
        for key, value in request.POST.items():
            if key == "csrfmiddlewaretoken" or not value:
                continue
            label = key.replace("_", " ").title()
            lines.append(f"{label}: {value}")

        message_text = "ATS-Friendly Resume Form Submission\n\n" + "\n".join(lines)

        inquiry = ContactInquiry(
            name=full_name or "Unknown",
            email=email or "",
            message=message_text,
            submission_type="ats_resume",
            ip_address=get_client_ip(request),
        )

        # Try to attach the ATS service if it exists
        ats_service = Service.objects.filter(slug="ats-resume").first()
        if ats_service:
            inquiry.service = ats_service
            inquiry.service_name = ats_service.name

        inquiry.save()
        messages.success(
            request,
            "Your details have been submitted! Complete payment to confirm your ATS resume order.",
        )

        payment_url = reverse("payment")
        if ats_service:
            payment_url = f"{payment_url}?service_slug={ats_service.slug}&order_type=inquiry&record_id={inquiry.id}"
        return redirect(payment_url)

    return render(request, "core/ats_resume_form.html")


def combo_pack_form(request):
    """Combo Pack intake form (covers resume + portfolio + profile needs)"""
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        # Build a structured message from submitted fields
        lines = []
        for key, value in request.POST.items():
            if key == "csrfmiddlewaretoken" or not value:
                continue
            label = key.replace("_", " ").title()
            lines.append(f"{label}: {value}")

        message_text = "Combo Pack Form Submission\n\n" + "\n".join(lines)

        inquiry = ContactInquiry(
            name=full_name or "Unknown",
            email=email or "",
            message=message_text,
            submission_type="combo_pack",
            ip_address=get_client_ip(request),
        )

        combo_service = Service.objects.filter(is_active=True, is_combo=True).first()
        if combo_service:
            inquiry.service = combo_service
            inquiry.service_name = combo_service.name

        inquiry.save()
        messages.success(
            request,
            "Thanks! Your combo pack request is in. Proceed to payment to confirm your order.",
        )

        payment_url = reverse("payment")
        if combo_service:
            payment_url = f"{payment_url}?service_slug={combo_service.slug}&order_type=inquiry&record_id={inquiry.id}"
        return redirect(payment_url)

    return render(request, "core/combo_pack_form.html")


def payment_page(request):
    """Payment handoff page (works for any service)"""
    service_slug = request.GET.get("service_slug")
    order_type = request.GET.get("order_type")
    record_id = request.GET.get("record_id")
    selected_service = None

    if service_slug:
        selected_service = Service.objects.filter(
            slug=service_slug, is_active=True
        ).first()

    # Fallback to combo service
    if not selected_service:
        selected_service = Service.objects.filter(is_active=True, is_combo=True).first()

    return render(
        request,
        "core/payment.html",
        {
            "selected_service": selected_service,
            # keep old name for template backward-compatibility
            "combo_service": selected_service,
            "razorpay_key": os.environ.get("RAZORPAY_KEY_ID", ""),
            "order_type": order_type or "",
            "record_id": record_id or "",
        },
    )


@csrf_exempt
def create_razorpay_order(request):
    """Create a Razorpay order and return order details for checkout"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        body = {}

    service_slug = body.get("service_slug") or request.POST.get("service_slug")
    order_type = body.get("order_type") or request.POST.get("order_type")
    record_id = body.get("record_id") or request.POST.get("record_id")

    selected_service = None
    if service_slug:
        selected_service = Service.objects.filter(
            slug=service_slug, is_active=True
        ).first()

    if not selected_service:
        selected_service = Service.objects.filter(is_active=True, is_combo=True).first()

    if not selected_service:
        return JsonResponse({"error": "Service not configured"}, status=400)

    key_id = os.environ.get("RAZORPAY_KEY_ID")
    key_secret = os.environ.get("RAZORPAY_KEY_SECRET")
    if not key_id or not key_secret:
        return JsonResponse({"error": "Razorpay keys missing"}, status=500)

    try:
        amount_paise = int(Decimal(selected_service.price) * 100)
    except Exception:
        return JsonResponse({"error": "Invalid service amount"}, status=400)

    auth_str = f"{key_id}:{key_secret}"
    auth_header = base64.b64encode(auth_str.encode()).decode()

    payload = {
        "amount": amount_paise,
        "currency": "INR",
        "receipt": f"{selected_service.slug}_{selected_service.id}",
        "payment_capture": 1,
        "notes": {
            "service": selected_service.name,
            "order_type": order_type or "",
            "record_id": str(record_id or ""),
        },
    }

    req = urlrequest.Request(
        "https://api.razorpay.com/v1/orders",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_header}",
        },
        method="POST",
    )

    try:
        with urlrequest.urlopen(req, timeout=10) as res:
            body = res.read().decode()
            data = json.loads(body)
            return JsonResponse(
                {
                    "order_id": data.get("id"),
                    "amount": data.get("amount"),
                    "currency": data.get("currency"),
                    "razorpay_key": key_id,
                    "order_type": order_type,
                    "record_id": record_id,
                }
            )
    except HTTPError as e:
        return JsonResponse(
            {"error": "Failed to create order", "details": e.read().decode()},
            status=500,
        )
    except URLError as exc:
        return JsonResponse(
            {"error": "Network error creating order", "details": str(exc)}, status=500
        )


@csrf_exempt
def payment_confirm(request):
    """Mark an order/inquiry as paid, generate invoice PDF, and email the customer."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        body = {}

    order_type = body.get("order_type")
    record_id = body.get("record_id")
    payment_id = body.get("razorpay_payment_id") or body.get("payment_id")
    razorpay_order_id = body.get("razorpay_order_id")

    if not order_type or not record_id or not payment_id:
        return JsonResponse({"error": "Missing payment details"}, status=400)

    customer_name = ""
    customer_email = ""
    service_name = ""
    amount_paid = Decimal("0")

    if order_type == "portfolio":
        from orders.models import PortfolioOrder

        order = get_object_or_404(PortfolioOrder, id=record_id)
        service = Service.objects.filter(slug="portfolio-website").first()
        if service:
            amount_paid = Decimal(service.price)
            order.amount_paid = amount_paid
        else:
            amount_paid = order.amount_paid
        order.payment_status = "paid"
        order.save(update_fields=["payment_status", "amount_paid", "updated_at"])

        customer_name = order.full_name
        customer_email = order.email
        service_name = service.name if service else "Portfolio Website"

    elif order_type == "inquiry":
        inquiry = get_object_or_404(ContactInquiry, id=record_id)
        service = inquiry.service
        if service:
            amount_paid = Decimal(service.price)
            inquiry.amount_paid = amount_paid
            service_name = service.name
        inquiry.payment_status = "paid"
        inquiry.status = "completed"
        inquiry.save(
            update_fields=["payment_status", "status", "amount_paid", "updated_at"]
        )

        customer_name = inquiry.name
        customer_email = inquiry.email
        service_name = service_name or inquiry.service_name or "Service"
    else:
        return JsonResponse({"error": "Invalid order type"}, status=400)

    # Generate invoice
    invoice_buffer = generate_payment_invoice(
        customer_name=customer_name or "Customer",
        service_name=service_name,
        amount=amount_paid,
        payment_id=payment_id,
        razorpay_order_id=razorpay_order_id,
    )

    # Email invoice
    subject = f"Payment received for {service_name}"
    body = (
        f"Hi {customer_name},\n\n"
        f"Thanks for your payment for {service_name}. Your payment ID is {payment_id}.\n"
        f"We've attached your invoice.\n\n"
        "If you have any questions, just reply to this email.\n\n"
        "— Nexio Labs Team"
    )
    try:
        email = EmailMessage(subject=subject, body=body, to=[customer_email])
        email.attach("invoice.pdf", invoice_buffer.getvalue(), "application/pdf")
        email.send(fail_silently=True)
    except Exception:
        # Fail silently but still return success
        pass

    return JsonResponse({"success": True})


def admin_login(request):
    """Admin login view"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Hardcoded credentials as requested
        if username == "nexiolabs" and password == "bhargav":
            # Create or get admin user
            from django.contrib.auth.models import User

            try:
                user = User.objects.get(username="admin")
            except User.DoesNotExist:
                user = User.objects.create_superuser(
                    "admin", "admin@nexiolabs.com", "bhargav"
                )

            user = authenticate(request, username="admin", password=password)
            if user is None:
                # Set password if not set
                user = User.objects.get(username="admin")
                user.set_password(password)
                user.save()
                user = authenticate(request, username="admin", password=password)

            if user:
                login(request, user)
                return redirect("admin_dashboard")

        messages.error(request, "Invalid credentials")

    return render(request, "core/admin_login.html")


@login_required
@ensure_csrf_cookie
def admin_dashboard(request):
    """Admin dashboard view"""
    from orders.models import PortfolioOrder

    try:
        portfolio_orders = PortfolioOrder.objects.all().order_by("-created_at")
        service_submissions = (
            ContactInquiry.objects.select_related("service")
            .filter(submission_type__in=["ats_resume", "combo_pack"])
            .order_by("-created_at")
        )
        inquiries = ContactInquiry.objects.filter(submission_type="inquiry").order_by(
            "-created_at"
        )
        portfolio_stats = portfolio_orders.aggregate(
            total=Count("id"),
            pending=Count("id", filter=Q(status="pending")),
            completed=Count("id", filter=Q(status="completed")),
        )
    except OperationalError:
        portfolio_orders = []
        service_submissions = []
        inquiries = []
        portfolio_stats = {"total": 0, "pending": 0, "completed": 0}

    # Ensure we use list() for portfolio_orders to prevent evaluation later if it's a QuerySet
    all_orders = list(portfolio_orders) + list(service_submissions)
    all_orders.sort(key=lambda x: getattr(x, 'created_at', None), reverse=True)

    # Safely calculate stats even if the database is not ready or tables are missing
    new_inquiries_count = 0
    if hasattr(inquiries, "filter"):
        try:
            # Check for inquiries with status 'new' if the field exists
            new_inquiries_count = inquiries.filter(status="new").count()
        except Exception:
            # Fallback if 'status' field doesn't exist yet
            new_inquiries_count = inquiries.count() if hasattr(inquiries, "count") else 0

    context = {
        "orders": portfolio_orders,
        "service_submissions": service_submissions,
        "all_orders": all_orders,
        "inquiries": inquiries,
        "new_inquiries": new_inquiries_count,
        "total_orders": portfolio_stats["total"] + (len(service_submissions) if isinstance(service_submissions, list) else getattr(service_submissions, "count", lambda: 0)()),
        "pending_orders": portfolio_stats["pending"],
        "completed_orders": portfolio_stats["completed"],
    }
    return render(request, "core/admin_dashboard.html", context)


def admin_logout_view(request):
    """Logout view for admin"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


def about(request):
    """About us page"""
    return render(request, "core/about.html")


def privacy_policy(request):
    """Privacy policy page"""
    return render(request, "core/privacy_policy.html")


def terms_of_service(request):
    """Terms of service page"""
    return render(request, "core/terms_of_service.html")


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@login_required
def download_inquiry_pdf(request, inquiry_id):
    """Download PDF for a contact inquiry"""
    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    pdf_buffer = generate_inquiry_pdf(inquiry)

    response = HttpResponse(pdf_buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="inquiry_{inquiry.id}_{inquiry.name.replace(" ", "_")}.pdf"'
    )
    return response


@login_required
def download_order_pdf(request, order_id):
    """Download PDF for a portfolio order"""
    from orders.models import PortfolioOrder

    order = get_object_or_404(PortfolioOrder, id=order_id)
    pdf_buffer = generate_portfolio_order_pdf(order)

    response = HttpResponse(pdf_buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="order_{order.id:05d}_{order.full_name.replace(" ", "_")}.pdf"'
    )
    return response


@login_required
def update_inquiry_status(request, inquiry_id):
    """Update the status of a contact inquiry (used by admin dashboard)"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    new_status = request.POST.get("status", "read")

    valid_statuses = {choice[0] for choice in ContactInquiry.STATUS_CHOICES}
    if new_status not in valid_statuses:
        return JsonResponse({"error": "Invalid status"}, status=400)

    inquiry.status = new_status
    inquiry.save(update_fields=["status", "updated_at"])

    return JsonResponse(
        {
            "success": True,
            "status": inquiry.status,
            "updated_at": inquiry.updated_at.strftime("%b %d, %Y at %H:%M"),
        }
    )
