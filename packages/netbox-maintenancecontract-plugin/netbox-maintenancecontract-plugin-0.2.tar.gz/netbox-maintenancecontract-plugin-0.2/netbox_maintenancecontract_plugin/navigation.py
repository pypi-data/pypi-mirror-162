from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_maintenancecontract_plugin:supplier_list',
        link_text='Supplier',
        buttons= [PluginMenuButton(
            link='plugins:netbox_maintenancecontract_plugin:supplier_add',
            title='Add',
            icon_class='mdi mdi-plus-thick',
            color=ButtonColorChoices.GREEN,
            permissions=["netbox_maintenancecontract_plugin.add_supplier"],
        )],
        permissions=["netbox_maintenancecontract_plugin.view_supplier"],
    ),
    PluginMenuItem(
        link='plugins:netbox_maintenancecontract_plugin:contract_list',
        link_text='Contracts',
        buttons= [PluginMenuButton(
            link='plugins:netbox_maintenancecontract_plugin:contract_add',
            title='Add',
            icon_class='mdi mdi-plus-thick',
            color=ButtonColorChoices.GREEN,
            permissions=["netbox_maintenancecontract_plugin.add_contract"],
        )],
        permissions=["netbox_maintenancecontract_plugin.view_supplier"],
    ),
    PluginMenuItem(
        link='plugins:netbox_maintenancecontract_plugin:contractdevice_list',
        link_text='Devices',
        buttons= [
            PluginMenuButton(
                link='plugins:netbox_maintenancecontract_plugin:contractdevice_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_maintenancecontract_plugin.add_contractdevice"],
            ),
            PluginMenuButton(
                "plugins:netbox_maintenancecontract_plugin:contractdevice_import",
                "Import",
                "mdi mdi-upload",
                ButtonColorChoices.CYAN,
                permissions=["netbox_maintenancecontract_plugin.add_contractdevice"],
            )
        ],
        permissions=["netbox_maintenancecontract_plugin.view_contractdevice"],

    ),
    
)
