from rest_framework_nested import routers
from .views import  DriverViewSet, EventViewSet, FuelLogViewSet, HeartbeatViewSet, InsuranceViewSet, VehicleAssignmentViewSet, VehicleLocationViewSet, VehicleOdometerViewSet, VehicleValueViewSet, VehicleViewSet, ViolationAnnotationViewSet, ViolationViewSet
router = routers.DefaultRouter()
router.register(r"vehicle", VehicleViewSet, basename="vehicle")
router.register(r"driver", DriverViewSet)
router.register(r"event", EventViewSet)
router.register(r"heartbeat", HeartbeatViewSet)
router.register(r"violation", ViolationViewSet)
router.register(r"violation-annotation", ViolationAnnotationViewSet)

vehicle_router = routers.NestedDefaultRouter(router, r"vehicle", lookup="vehicle")
vehicle_router.register(r"insurance", InsuranceViewSet, basename="vehicle-insurance")
vehicle_router.register(r"fuel-log", FuelLogViewSet, basename="vehicle-fuel-log")
vehicle_router.register(r"odometers", VehicleOdometerViewSet, basename="vehicle-odometers")
vehicle_router.register(r"locations", VehicleLocationViewSet, basename="vehicle-locations")
vehicle_router.register(r"assignments", VehicleAssignmentViewSet, basename="vehicle-assignments")
vehicle_router.register(r"values", VehicleValueViewSet, basename="vehicle-values")

urlpatterns = router.urls + vehicle_router.urls