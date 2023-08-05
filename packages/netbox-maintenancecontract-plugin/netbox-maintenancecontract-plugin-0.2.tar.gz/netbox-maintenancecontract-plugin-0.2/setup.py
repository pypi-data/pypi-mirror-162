from setuptools import find_packages, setup

setup(
    name='netbox-maintenancecontract-plugin',
    version='0.2',
    download_url='',
    description='Manage Maintenance Contracts Netbox',
    install_requires=[],
    packages=['netbox_maintenancecontract_plugin','netbox_maintenancecontract_plugin.api'],
    include_package_data=True,
    zip_safe=False,
)
