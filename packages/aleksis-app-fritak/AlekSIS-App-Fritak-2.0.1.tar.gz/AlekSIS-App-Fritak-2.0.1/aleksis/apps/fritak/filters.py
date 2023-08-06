from django.db.models import Count
from django.utils.translation import gettext_lazy as _

import django_filters

from aleksis.core.models import Person

from .models import ExemptionRequest


def get_exemption_persons():
    """Find all users who sent a exemption request."""
    persons = Person.objects.filter(exemption_requests__isnull=False).annotate(
        exemption_requests_count=Count("exemption_requests")
    )
    return persons


class ExemptionFilter(django_filters.FilterSet):
    submitter = django_filters.ModelChoiceFilter(
        label=_("Submitter"), queryset=get_exemption_persons()
    )

    class Meta:
        model = ExemptionRequest
        fields = [
            "submitter",
        ]
