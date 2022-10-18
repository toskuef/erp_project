from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('crm.urls', namespace='crm')),
    path('admin/', admin.site.urls),
]
