from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('ats-resume/', views.ats_resume_form, name='ats_resume_form'),
    path('combo-pack/', views.combo_pack_form, name='combo_pack_form'),
    path('payment/', views.payment_page, name='payment'),
    path('payment/order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('payment/confirm/', views.payment_confirm, name='payment_confirm'),
    path('custom-project/', views.custom_project, name='custom_project'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout_view, name='admin_logout'),
    path('download/inquiry/<int:inquiry_id>/', views.download_inquiry_pdf, name='download_inquiry_pdf'),
    path('download/order/<int:order_id>/', views.download_order_pdf, name='download_order_pdf'),
    path('admin/messages/<int:inquiry_id>/status/', views.update_inquiry_status, name='update_inquiry_status'),
]
