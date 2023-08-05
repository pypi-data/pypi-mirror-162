from django.urls import path

from netbox.views.generic import ObjectChangeLogView
from . import models, views

urlpatterns = (

   # Supplier
    path('supplier/', views.SupplierListView.as_view(), name='supplier_list'),
    path('supplier/add/', views.SupplierEditView.as_view(), name='supplier_add'),
    path('supplier/<int:pk>/', views.SupplierView.as_view(), name='supplier'),
    path('supplier/<int:pk>/edit/', views.SupplierEditView.as_view(), name='supplier_edit'),
    path('supplier/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    path('supplier/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='supplier_changelog', kwargs={ 'model': models.Supplier}),

    # Contracts
    path('contract/', views.ContractListView.as_view(), name='contract_list'),
    path('contract/add/', views.ContractEditView.as_view(), name='contract_add'),
    path('contract/<int:pk>/', views.ContractView.as_view(), name='contract'),
    path('contract/<int:pk>/edit/', views.ContractEditView.as_view(), name='contract_edit'),
    path('contract/<int:pk>/delete/', views.ContractDeleteView.as_view(), name='contract_delete'),
    path('contract/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='contract_changelog', kwargs={ 'model': models.Contract}),

     # Devices
    path('contractdevice/', views.ContractDeviceListView.as_view(), name='contractdevice_list'),
    path('contractdevice/add/', views.ContractDeviceEditView.as_view(), name='contractdevice_add'),
    path("contractdevice/import/", views.ContractDeviceBulkImportView.as_view(), name="contractdevice_import"),
    path('contractdevice/<int:pk>/', views.ContractDeviceView.as_view(), name='contractdevice'),
    path('contractdevice/<int:pk>/edit/', views.ContractDeviceEditView.as_view(), name='contractdevice_edit'),
    path('contractdevice/<int:pk>/delete/', views.ContractDeviceDeleteView.as_view(), name='contractdevice_delete'),
    path('contractdevice/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='contractdevice_changelog', kwargs={ 'model': models.ContractDevice}),

  

)