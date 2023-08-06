import django_filters
from django.db.models import Q

from nautobot.utilities.choices import ColorChoices
from nautobot.utilities.filters import BaseFilterSet
from nautobot.tenancy.models import Tenant

from .models import CableTemplate, CablePlug


class CableTemplateFilterSet(BaseFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    color = django_filters.MultipleChoiceFilter(
        choices=ColorChoices
    )

    owner_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label="Owner (ID)",
    )
    owner = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name="owner__slug",
        to_field_name="slug",
        label="Owner (Slug)",
    )

    plug_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CablePlug.objects.all(),
        label="Plug (ID)",
    )
    plug = django_filters.ModelMultipleChoiceFilter(
        queryset=CablePlug.objects.all(),
        field_name="plug__name",
        to_field_name="name",
        label="Plug (Name)",
    )

    class Meta:
        model = CableTemplate
        fields = ['cable_number', 'type', 'color']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(cable_number__icontains=value) |
            Q(label__icontains=value)
        )
        return queryset.filter(qs_filter)
