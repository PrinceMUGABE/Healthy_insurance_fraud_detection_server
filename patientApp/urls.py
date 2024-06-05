from django.urls import path
from . import views

urlpatterns = [
    path('clients/', views.display_clients, name='clients'),
    # path('create/', views.get_create_client_page, name='create_client'),
    path('save_member', views.save_insurance_member, name='save_member'),
    path('edit/<int:client_id>/', views.edit_client, name='edit_client'),
    path('update/<int:client_id>/', views.update, name='update'),
    path('delete/<int:client_id>/', views.delete_client, name='delete_client'),
    path('clients/<int:client_id>/', views.view_client_details, name='client_details'),
    
    path('total/', views.total_clients, name='total_clients'),
    path('increase_2024/', views.clients_in_2024, name='clients_in_2024'),
    path('increase_may/', views.clients_in_may, name='clients_in_may'),
    path('download/pdf/', views.download_clients_pdf, name='download_clients_pdf'),
    path('download/excel/', views.download_clients_excel, name='download_clients_excel'),
    path('new_today/', views.new_clients_today, name='new_clients_today'),
    path('search/', views.search_clients, name='search_clients'),

]
