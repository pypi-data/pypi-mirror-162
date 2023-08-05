from rest_framework import serializers
from ipam.api.serializers import NestedPrefixSerializer
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from ..models import Contract, ContractDevice, Supplier

class ContractSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_maintenancecontract_plugin-api:contract-detail'
    )

    class Meta:
        model = Contract
        fields = (
            'id', 'url','display',
            'status', 'supplier', 'description', 'contract_number', 'start_of_contract', 'end_of_contract', 'status', 'comments',
            'custom_fields', 'created',
            'last_updated',
        )

class ContractDeviceSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_maintenancecontract_plugin-api:contractdevice-detail'
    )

    class Meta:
        model = ContractDevice
        fields = (
            'id', 'url','pk','display',
            'device','contract',
            'custom_fields', 'created',
            'last_updated',
        )

class SupplierSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_maintenancecontract_plugin-api:supplier-detail'
    )

    class Meta:
        model = Supplier
        fields = (
            'id', 'url','pk', "name",
        "physical_address",
        "country",
        "phone",
        "email",
        "portal_url",
        "comments",
            'custom_fields', 'created',
            'last_updated',
        )

