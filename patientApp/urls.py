from django.urls import path
from . import views

urlpatterns = [
    path('clients/', views.display_clients, name='clients'),
    path('save/', views.save_insurance_member, name='save_member'),
    path('get_client/<int:client_id>/', views.get_client, name='get_client'),
    path('update_client/<int:client_id>/', views.update_client, name='update_client'),
    path('delete/<int:client_id>/', views.delete_client, name='delete_client'),    
    path('total/', views.total_clients, name='total_clients'),
    path('increase_2024/', views.clients_in_2024, name='clients_in_2024'),
    path('increase_may/', views.clients_in_may, name='clients_in_may'),
    path('download/pdf/', views.download_clients_pdf, name='download_clients_pdf'),
    path('download/excel/', views.download_clients_excel, name='download_clients_excel'),
    path('new_today/', views.new_clients_today, name='new_clients_today'),
    path('search/', views.search_clients, name='search_clients'),

]
