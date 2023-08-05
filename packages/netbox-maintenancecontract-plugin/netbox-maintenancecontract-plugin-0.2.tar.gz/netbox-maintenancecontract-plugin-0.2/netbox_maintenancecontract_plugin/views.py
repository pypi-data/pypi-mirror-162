from django.db.models import Count

from netbox.views import generic
from . import filtersets, forms, models, tables

#
# MaintenanceContractDevice views
#

class ContractDeviceView(generic.ObjectView):
    queryset = models.ContractDevice.objects.all()

class ContractDeviceListView(generic.ObjectListView):
    queryset = models.ContractDevice.objects.annotate()
    table = tables.ContractDeviceTable

class ContractDeviceEditView(generic.ObjectEditView):
    queryset = models.ContractDevice.objects.all()
    form = forms.ContractDeviceForm

class ContractDeviceDeleteView(generic.ObjectDeleteView):
    queryset = models.ContractDevice.objects.all()

class ContractDeviceBulkImportView(generic.BulkImportView):
    queryset = models.ContractDevice.objects.all().prefetch_related(
        'device','contract'
    )
    model_form = forms.ContractDeviceCSVForm
    table = tables.ContractDeviceTable


#
# MaintenanceContract views
#

class ContractView(generic.ObjectView):
    queryset = models.Contract.objects.all()
    def get_extra_context(self, request, instance):
        table = tables.ContractDeviceTable(instance.devices.all())
        table.configure(request)

        return {
            'device_table': table,
        }

class ContractListView(generic.ObjectListView):
    queryset = models.Contract.objects.annotate(
        device_count=Count('devices')
    )
    table = tables.ContractTable

class ContractEditView(generic.ObjectEditView):
    queryset = models.Contract.objects.all()
    form = forms.ContractForm

class ContractDeleteView(generic.ObjectDeleteView):
    queryset = models.Contract.objects.all()



#
# supplier views
#

class SupplierView(generic.ObjectView):
    queryset = models.Supplier.objects.all()
    def get_extra_context(self, request, instance):
        table = tables.ContractTable(instance.contracts.all())
        table.configure(request)

        return {
            'contract_table': table,
        }


class SupplierListView(generic.ObjectListView):
    queryset = models.Supplier.objects.annotate(
        contract_count=Count('contracts')
    )
    table = tables.SupplierTable

class SupplierEditView(generic.ObjectEditView):
    queryset = models.Supplier.objects.all()
    form = forms.SupplierForm

class SupplierDeleteView(generic.ObjectDeleteView):
    queryset = models.Supplier.objects.all()


