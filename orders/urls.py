from django.urls import path
from . import views

urlpatterns = [
    path('portfolio/', views.portfolio_order, name='portfolio_order'),
    path('api/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
