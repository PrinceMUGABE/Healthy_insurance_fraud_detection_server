from django.urls import path
from . import views
from .views import search_predictions, delete_prediction
from .views import download_predictions_pdf, download_predictions_excel
from .views import institution_predictions, total_available_predictions
from .views import increase_of_predictions_2024, increase_of_predictions_last_5_years

urlpatterns = [
    path('predictions/', views.display_predictions, name='predictions'),
    #path('create_prediction/', views.get_create_prediction_page, name='create_prediction'),  # Updated name
    path('save_prediction/', views.save_prediction, name='save_prediction'),  # Added trailing slash for consistency
    path('search_predictions/', search_predictions, name='search_predictions'),
    path('delete/<int:prediction_id>/', delete_prediction, name='delete_prediction'),
    path('download/pdf/', download_predictions_pdf, name='download_predictions_pdf'),
    path('download/excel/', download_predictions_excel, name='download_predictions_excel'),
    path('institution-predictions/', institution_predictions, name='institution_predictions'),
    path('total-available-predictions/', total_available_predictions, name='total_available_predictions'),
    path('increase_2024/', increase_of_predictions_2024, name='increase_of_predictions_2024'),
    path('increase_last_5_years/', increase_of_predictions_last_5_years, name='increase_of_predictions_last_5_years'),

]

