from django.urls import path
from . import views

urlpatterns = [
    # Existing URL patterns
    path('signup/', views.get_signup_page, name='signup'),
    path('create/', views.create_user, name='create'),
    path('signin/', views.signin, name='signin'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('investigator_dashboard/', views.investigator_dashboard, name='investigator_dashboard'),
    path('users/', views.list_users, name='list_users'),
    path('update/<int:user_id>/', views.update_user_data, name='update_user_data'),
    path('logout/', views.logout_user, name='logout'),
    path('saveUserUpdate/', views.update_user_data, name='update_user'),
    path('today/', views.today_users, name='today_users'),
]
