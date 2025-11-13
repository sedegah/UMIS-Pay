from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_dashboard, name='bankreports_dashboard'),
    path('api/daily-report/', views.daily_report_api, name='bankreports_api'),
    
    path('export/csv/', views.export_daily_csv, name='bankreports_csv'),
    
    path('export-csv/', views.export_daily_csv, name='bankreports_csv_dash'),
]
