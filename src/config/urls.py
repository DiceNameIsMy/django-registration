from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('health/', include('utils.health.urls')),

        path('v1/', include([
            path('accounts/', include('accounts.api.v1.urls', namespace='v1')),
        ])),
    ])),
]
