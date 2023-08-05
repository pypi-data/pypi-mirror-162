from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from datetime import datetime, date

from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet


class StatusChoices(ChoiceSet):
    key = 'Contract.status'

    CHOICES = [
        ('offered', 'Offered', 'orange'),
        ('active', 'Active', 'green'),
        ('expired', 'Expired', 'red'),
    ]

class Supplier(NetBoxModel):

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)
    physical_address = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=3, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True, verbose_name="E-mail")
    portal_url = models.URLField(blank=True, verbose_name="Portal URL")
    comments = models.TextField(blank=True)

    csv_headers = [
        "name",
        "description",
        "physical_address",
        "country",
        "phone",
        "email",
        "portal_url",
        "comments",
    ]

    class Meta:
        """Meta attributes for the class."""
        ordering = ("name",)

    def __str__(self):
        """String representation of ProviderLCM."""
        return self.name

    def get_absolute_url(self):
        """Returns the Detail view for ProviderLCM models."""
        return reverse("plugins:netbox_maintenancecontract_plugin:supplier", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        """Override save to assert a full clean."""
        # Full clean to assert custom validation in clean() for ORM, etc.
        super().full_clean()
        super().save(*args, **kwargs)

    def to_csv(self):
        """Return fields for bulk view."""
        return (
            self.name,
            self.description,
            self.physical_address,
            self.country,
            self.phone,
            self.email,
            self.portal_url,
            self.comments,
        )


class Contract(NetBoxModel):

    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.PROTECT,
        help_text="Name of Maintenance contract supplier",
        related_name='contracts'
    )

    description = models.CharField(
        max_length=200, 
        blank=True,
        null=True
    )

    contract_number = models.CharField(
        max_length=100,
        help_text="Supplier provided Contract number",
    )

    start_of_contract = models.DateField(
        help_text="start of contract",
        blank=True,
        null=True
    )

    end_of_contract = models.DateField(
        help_text="end of contract",
        blank=True,
        null=True

    )
       
    @property
    def status(self):
        if date.today() > self.start_of_contract and date.today() < self.end_of_contract:
            return "active"

        if date.today() < self.start_of_contract:
            return "offered"

        if date.today() > self.end_of_contract:
            return "expired"

    comments = models.TextField(
        blank=True,
        help_text=""
    )

    def __str__(self):
        return f'{self.contract_number} ({self.supplier})'

    def get_absolute_url(self):
        return reverse('plugins:netbox_maintenancecontract_plugin:contract', args=[self.pk])

    def get_status_color(self):
        return StatusChoices.colors.get(self.status)

    class Meta:
        ordering = ('supplier',)
        unique_together = ('supplier', 'contract_number')

class ContractDevice(NetBoxModel):
    def __str__(self):
        return f'{self.device}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_maintenancecontract_plugin:contractdevice', args=[self.pk])

    device = models.OneToOneField(
        to="dcim.Device", 
        on_delete=models.CASCADE, 
    )
   
    contract = models.ForeignKey(
        Contract, 
        on_delete=models.PROTECT,
        related_name='devices'
        )

    updated_at = models.DateTimeField(auto_now=True)

