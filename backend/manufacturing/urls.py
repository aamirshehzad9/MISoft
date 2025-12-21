from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (WorkCenterViewSet, BillOfMaterialsViewSet, BOMItemViewSet, BOMOperationViewSet,
                    ProductionOrderViewSet, MaterialConsumptionViewSet, QualityCheckViewSet,
                    ProductionDowntimeViewSet)

router = DefaultRouter()
router.register(r'work-centers', WorkCenterViewSet, basename='workcenter')
router.register(r'bom', BillOfMaterialsViewSet, basename='bom')
router.register(r'bom-items', BOMItemViewSet, basename='bomitem')
router.register(r'bom-operations', BOMOperationViewSet, basename='bomoperation')
router.register(r'production-orders', ProductionOrderViewSet, basename='productionorder')
router.register(r'material-consumption', MaterialConsumptionViewSet, basename='materialconsumption')
router.register(r'quality-checks', QualityCheckViewSet, basename='qualitycheck')
router.register(r'downtimes', ProductionDowntimeViewSet, basename='downtime')

urlpatterns = [
    path('', include(router.urls)),
]
