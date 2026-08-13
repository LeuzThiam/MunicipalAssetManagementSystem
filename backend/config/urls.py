from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('common.urls')),
    path('api/', include('assets.urls')),
]