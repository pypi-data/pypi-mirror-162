from extras.plugins import PluginConfig

class NetBoxMaintenanceContract(PluginConfig):
    name = 'netbox_maintenancecontract_plugin'
    verbose_name = 'maintenance'
    author = "Henrik Hansen"
    author_email = "henrik.hansen@cgi.com"
    description = 'CGI Plugin'
    version = '0.1'
    base_url = 'maintenance'
    
config = NetBoxMaintenanceContract
