from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_user, name='signup'),
    path('login/', views.get_login_page, name='login'),
    path('signin/', views.signin, name='signin'),
    path('user/admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('investigator_dashboard/', views.investigator_dashboard, name='investigator_dashboard'),
    path('user/users/', views.list_users, name='list_users'),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user/<int:user_id>/', views.get_user, name='get_user'),
    path('logout/', views.logout_user, name='logout'),
    path('user/today/', views.today_users, name='today_users'),
    path('user/users/download/pdf/', views.download_users_pdf, name='download_users_pdf'),
    path('user/users/download/excel/', views.download_users_excel, name='download_users_excel'),
    
    
    path('prediction-trends/', views.prediction_trends, name='prediction_trends'),
    path('prediction/available_predictions_today/', views.available_predictions_today, name='available_predictions_today'),
]
