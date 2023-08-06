from django.db import models

from nautobot.dcim.choices import *
from nautobot.dcim.models import Cable
from nautobot.utilities.fields import ColorField
from nautobot.utilities.querysets import RestrictedQuerySet
from nautobot.core.models import BaseModel


class CablePlug(BaseModel):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

    def __str__(self):
        return self.name


class CableTemplate(BaseModel):
    cable_number = models.CharField(
        max_length=50,
        unique=True,
    )
    type = models.CharField(
        max_length=50,
        choices=CableTypeChoices,
        blank=True
    )
    plug = models.ForeignKey(
        to=CablePlug,
        on_delete=models.CASCADE,
        related_name="cable_templates",
        blank=True,
        null=True,
    )
    label = models.CharField(
        max_length=100,
        blank=True
    )
    color = ColorField(
        blank=True
    )
    length = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )
    length_unit = models.CharField(
        max_length=50,
        choices=CableLengthUnitChoices,
        blank=True,
    )
    cable = models.OneToOneField(
        Cable,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    owner = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.CASCADE,
        related_name="cable_templates",
        blank=True,
        null=True,
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = [
        'cable_number', 'owner', 'type', 'plug', 'label', 'color', 'length', 'length_unit',
    ]

    def __str__(self):
        return self.cable_number


class MeasurementLog(BaseModel):
    link = models.URLField(
        blank=True,
        null=True
    )
    cable = models.OneToOneField(
        Cable,
        on_delete=models.CASCADE,
    )
