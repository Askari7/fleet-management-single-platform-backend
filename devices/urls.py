from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, VehicleDeviceHistoryViewSet

router = DefaultRouter()
router.register(r"device", DeviceViewSet, basename="device")
router.register(r'device-history', VehicleDeviceHistoryViewSet)
urlpatterns = router.urls