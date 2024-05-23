
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('userAccountApp.urls')),
    path('insurance/', include('insuranceApp.urls')),
    path('employee/', include('employeeApp.urls')),
    path('client/', include('patientApp.urls')),
    path('prediction/', include('insurancePredictionApp.urls')),
]
