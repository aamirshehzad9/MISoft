from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessPartnerViewSet

router = DefaultRouter()
router.register(r'', BusinessPartnerViewSet, basename='businesspartner')

urlpatterns = [
    path('', include(router.urls)),
]
