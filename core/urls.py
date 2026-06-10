from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('vendor/add-product/', views.vendor_add_product, name='vendor_add_product'),
    path('vendor/create-employee/', views.vendor_create_employee, name='vendor_create_employee'),
    path('checkout/<int:product_id>/', views.checkout_view, name='checkout'),
    path('order/<int:order_id>/ship/', views.update_status_shipper, name='update_status_shipper'),
    path('order/<int:order_id>/out-for-delivery/', views.update_status_out_for_delivery, name='update_status_out_for_delivery'),
    path('order/<int:order_id>/deliver/', views.verify_otp_and_deliver, name='verify_otp_and_deliver'),
    path('order/<int:order_id>/receipt/', views.generate_receipt_pdf, name='generate_receipt_pdf'),
    path('admin-portal/approve-vendor/<int:vendor_id>/', views.admin_approve_vendor, name='admin_approve_vendor'),
    path('admin-portal/disapprove-vendor/<int:vendor_id>/', views.admin_disapprove_vendor, name='admin_disapprove_vendor'),
    path('admin-portal/create-admin/', views.admin_create_admin, name='admin_create_admin'),
    path('admin-portal/export-audit-report/', views.export_audit_report_excel, name='export_audit_report_excel'),
]
