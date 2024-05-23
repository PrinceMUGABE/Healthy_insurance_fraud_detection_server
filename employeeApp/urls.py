from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.display_employees, name='employees'),
    path('create_employee/', views.get_create_employee_page, name='create'),
    path('save_employee', views.save_employee, name='save_employee'),
    path('edit/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('update/<int:employee_id>/', views.update, name='update'),
    path('delete/<int:employee_id>/', views.delete_employee, name='delete_employee'),

]
