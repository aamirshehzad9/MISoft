"""
Products URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UoMConversionViewSet, UnitOfMeasureViewSet, ProductViewSet, ProductVariantViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'variants', ProductVariantViewSet, basename='productvariant')
router.register(r'uom-conversions', UoMConversionViewSet, basename='uomconversion')
router.register(r'units-of-measure', UnitOfMeasureViewSet, basename='unitofmeasure')

urlpatterns = [
    path('', include(router.urls)),
]
