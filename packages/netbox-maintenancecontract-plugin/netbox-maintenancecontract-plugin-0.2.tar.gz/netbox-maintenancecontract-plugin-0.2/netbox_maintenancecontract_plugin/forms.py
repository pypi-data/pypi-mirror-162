from django import forms

from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm,NetBoxModelCSVForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField
from utilities.forms import CSVModelChoiceField
from .models import Contract, ContractDevice, Supplier
from dcim.models import Device


class ContractForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = Contract
        fields = ('supplier', 'description','contract_number','start_of_contract','end_of_contract','comments')


class SupplierForm(NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = Supplier
        fields = ('name', 'physical_address','country','phone','email','portal_url','comments')



class ContractDeviceForm(NetBoxModelForm):

    contract = DynamicModelChoiceField(
        queryset=Contract.objects.all()
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all()
    )

    class Meta:
        model = ContractDevice
        fields = ('contract','device')

class ContractDeviceCSVForm(NetBoxModelCSVForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=True,
        to_field_name="serial",
        help_text="serialnumber of device to add to contract",
        error_messages={
            "invalid_choice": "serialnumber not found.",
        }
    )

    class Meta:
        model = ContractDevice
        fields = (
            "contract",
            "device",
        )