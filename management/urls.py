from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('qr-scanner/', views.qr_scanner_page, name='qr_scanner_page'),
    path('temples/', views.admin_temple_list, name='admin_temple_list'),
    path('slots/', views.admin_slot_mgmt, name='admin_slot_mgmt'),
    path('sos-monitor/', views.admin_sos_monitor, name='admin_sos_monitor'),
    path('finance/', views.admin_finance, name='admin_finance'),
    # Add this specific line to fix the error:
    path('resolve-sos/<int:sos_id>/', views.resolve_sos, name='resolve_sos'),
    path('temples/add/', views.admin_temple_add, name='admin_temple_add'),
    path('temples/edit/<int:pk>/', views.admin_temple_edit, name='admin_temple_edit'),
    path('temples/delete/<int:pk>/', views.admin_temple_delete, name='admin_temple_delete'),
    path('slots/add/', views.admin_slot_add, name='admin_slot_add'),
    path('slots/edit/<int:pk>/', views.admin_slot_edit, name='admin_slot_edit'),
    path('slots/delete/<int:pk>/', views.admin_slot_delete, name='admin_slot_delete'),
    path('validate/<uuid:booking_uuid>/', views.validate_booking, name='validate_booking'),
    path('live-stats/', views.admin_live_stats, name='admin_live_stats'),
]