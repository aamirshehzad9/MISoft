from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductCategoryViewSet, UnitOfMeasureViewSet, ProductViewSet, ProductVariantViewSet

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet, basename='productcategory')
router.register(r'uom', UnitOfMeasureViewSet, basename='unitofmeasure')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'variants', ProductVariantViewSet, basename='productvariant')

urlpatterns = [
    path('', include(router.urls)),
]
