import django_tables2 as tables

from netbox.tables import NetBoxTable, ChoiceFieldColumn
from .models import Contract,ContractDevice,Supplier




class ContractTable(NetBoxTable):
    contract_number = tables.Column(
        linkify=True
    )
    status = ChoiceFieldColumn()
    device_count = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = Contract
        fields = ('pk','status', 'supplier','description','contract_number','start_of_contract','end_of_contract','device_count')
        default_columns = ('description','contract_number','start_of_contract','end_of_contract','device_count','')


class ContractDeviceTable(NetBoxTable):
   
    class Meta(NetBoxTable.Meta):
        model = ContractDevice
        fields = ('pk','device', 'contract')
        default_columns = ('pk','device', 'contract')
    
    device = tables.Column(
        linkify=True
    )
    contract = tables.Column(
        linkify=True
    )

class SupplierTable(NetBoxTable):
    name = tables.Column(
        linkify=True
    )

    contract_count = tables.Column()
    physical_address = tables.Column(
        linkify=True
    )
    
    class Meta(NetBoxTable.Meta):
        model = Supplier
        fields = ('pk','name','physical_address', 'contract_count')
        default_columns = ('name','physical_address', 'contract_count')
