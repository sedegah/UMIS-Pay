from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate_serial, name='generate_serial'),
    path('success/<int:serial_id>/', views.success, name='success'), 
    path('get-serial-data/', views.get_serial_data, name='get_serial_data'),
]