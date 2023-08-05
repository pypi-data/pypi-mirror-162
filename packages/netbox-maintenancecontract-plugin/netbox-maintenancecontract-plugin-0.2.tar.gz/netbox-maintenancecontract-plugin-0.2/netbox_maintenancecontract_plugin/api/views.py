from django.db.models import Count

from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import ContractDeviceSerializer, ContractSerializer ,SupplierSerializer


class ContractViewSet(NetBoxModelViewSet):
    queryset = models.Contract.objects.all()
    serializer_class = ContractSerializer

class ContractDeviceViewSet(NetBoxModelViewSet):
    queryset = models.ContractDevice.objects.all()
    serializer_class = ContractDeviceSerializer


class SupplierViewSet(NetBoxModelViewSet):
    queryset = models.Supplier.objects.all()
    serializer_class = SupplierSerializer

