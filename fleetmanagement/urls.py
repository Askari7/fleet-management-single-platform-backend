"""
URL configuration for fleetmanagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/api/', include("accounts.urls")),
    path('devices/api/', include("devices.urls")),
    path('vehicles/api/', include("fleet.urls")),
    path('drivers/api/', include("drivers.urls")),
    path('journeys/api/', include("journeys.urls")),
    path('maintenances/api/', include("maintenance.urls")),
    path('analytics/api/', include("analytics.urls")),
    path('inventory/api/', include("inventory.urls")),
    path('tyres/api/', include("tyres.urls")),
]
