from django.core.exceptions import ObjectDoesNotExist
from extras.plugins import PluginTemplateExtension
from django.conf import settings
from packaging import version
from .models import ContractDevice, Contract

class DeviceMaintenanceContractStatus(PluginTemplateExtension):
    model = "dcim.device"

    def left_page(self):
        device = self.context["object"]
     
        try:
            c_device = ContractDevice.objects.get(device=device)
            return self.render(
                "netbox_maintenancecontract_plugin/device.html", extra_context={
                    "cdevice": c_device
                    }
            )
        except:
             return self.render(
                "netbox_maintenancecontract_plugin/device.html", extra_context={}
            )

template_extensions = [DeviceMaintenanceContractStatus]