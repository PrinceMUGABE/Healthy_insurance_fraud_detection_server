from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.display_employees, name='employees'),
    path('create_employee/', views.get_create_employee_page, name='create'),
    path('save_employee/', views.save_employee, name='save_employee'),
    path('edit/<int:id>/', views.get_employee, name='edit_employee'),
    path('update/<int:employee_id>/', views.update_employee, name='update_employee'),
    path('delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('download_employees_pdf/', views.download_employees_pdf, name='download_employees_pdf'),
    path('download_employees_excel/', views.download_employees_excel, name='download_employees_excel'),
]
