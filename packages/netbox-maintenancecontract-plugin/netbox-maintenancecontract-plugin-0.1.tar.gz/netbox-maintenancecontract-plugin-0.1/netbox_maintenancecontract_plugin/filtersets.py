from netbox.filtersets import NetBoxModelFilterSet
from .models import Contract, ContractDevice


class ContractFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = Contract
        fields = ('supplier', 'contract_number')

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)
