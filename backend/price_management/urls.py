from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PriceRuleViewSet

router = DefaultRouter()
router.register(r'rules', PriceRuleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
