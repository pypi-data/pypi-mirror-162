from netbox.api.routers import NetBoxRouter
from . import views


app_name = 'netbox_maintenancecontract_plugin'

router = NetBoxRouter()
router.register('contract', views.ContractViewSet)
router.register('contractdevice', views.ContractDeviceViewSet)
router.register('supplier', views.SupplierViewSet)

urlpatterns = router.urls