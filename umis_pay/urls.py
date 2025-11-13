from django.contrib import admin
from django.urls import path, include
from serialgenerator import views
from bankreports import views as bank_views  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('generate/', views.generate_serial, name='generate_serial'),
    path('success/<int:serial_id>/', views.success, name='success'),

    path('bankreports/', include('bankreports.urls')),

    path('bankreports/export-csv/', bank_views.export_daily_csv, name='bankreports_csv_dash'),
    path('bankreports/export/csv/', bank_views.export_daily_csv, name='bankreports_csv_direct'),
]
