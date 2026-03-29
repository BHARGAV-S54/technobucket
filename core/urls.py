from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('ats-resume/', views.ats_resume_form, name='ats_resume_form'),
    path('combo-pack/', views.combo_pack_form, name='combo_pack_form'),
    path('payment/', views.payment_page, name='payment'),
    path('custom-project/', views.custom_project, name='custom_project'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout_view, name='admin_logout'),
]
