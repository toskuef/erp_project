from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('user/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('crm.urls', namespace='crm')),
    path('admin/', admin.site.urls),
]
