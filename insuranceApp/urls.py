from django.urls import path
from . import views

urlpatterns = [
    path('display/', views.display_insurances, name='display_insurances'),
    path('create/', views.get_create_insurance_page, name='create_insurance_page'),
    path('save/', views.save_insurance, name='save_insurance'),
    path('edit/<int:insurance_id>/', views.edit_insurance, name='edit_insurance'),
    path('update/<int:insurance_id>/', views.update, name='update_insurance'),
    path('delete/<int:insurance_id>/', views.delete_insurance, name='delete_insurance'),
    path('search/', views.search_insurance, name='search_insurance'),
    path('download/pdf/', views.download_insurance_pdf, name='download_insurance_pdf'),
    path('download/excel/', views.download_insurance_excel, name='download_insurance_excel'),
    path('increase/', views.increase_of_insurances, name='increase_of_insurances'),

]
