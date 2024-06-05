
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userAccountApp.urls')),
    path('insurance/', include('insuranceApp.urls')),
    path('employee/', include('employeeApp.urls')),
    path('client/', include('patientApp.urls')),
    path('prediction/', include('insurancePredictionApp.urls')),
]
