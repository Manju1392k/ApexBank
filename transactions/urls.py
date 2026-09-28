from django.urls import path
from . import views

urlpatterns = [
    # Customer Banking URLs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('transfer/', views.transfer_view, name='transfer'),
    path('statement/', views.statement_view, name='statement'),
    
    # AJAX validation API
    path('api/verify-account/', views.verify_account_api, name='verify_account_api'),
    
    # Admin Banking Portal URLs
    path('admin-portal/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-portal/deposit/', views.admin_deposit_view, name='admin_deposit'),
    path('admin-portal/deposit/<str:account_number>/', views.admin_deposit_view, name='admin_deposit_target'),
    path('admin-portal/account/<str:account_number>/', views.admin_account_detail_view, name='admin_account_detail'),
]
