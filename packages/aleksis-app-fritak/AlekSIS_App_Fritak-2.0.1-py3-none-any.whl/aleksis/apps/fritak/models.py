from datetime import date

from django.db import models
from django.urls import reverse
from django.utils import formats, timezone
from django.utils.translation import gettext_lazy as _

from aleksis.core.mixins import ExtensibleModel
from aleksis.core.models import Notification, Person


class Status:
    def __init__(self, name, style_class):
        self.name = name
        self.style_class = style_class

    def __str__(self):
        return self.name


status_list = [
    Status(name=_("In process 1"), style_class="orange"),
    Status(name=_("In process 2"), style_class="yellow"),
    Status(name=_("Approved"), style_class="green"),
    Status(name=_("Rejected"), style_class="red"),
]

status_choices = [(x, val.name) for x, val in enumerate(status_list)]


class ExemptionRequest(ExtensibleModel):
    # Time
    from_date = models.DateField(default=date.today, verbose_name=_("Start date"))
    from_time = models.TimeField(default=timezone.now, verbose_name=_("Start time"))
    to_date = models.DateField(default=date.today, verbose_name=_("End date"))
    to_time = models.TimeField(default=timezone.now, verbose_name=_("End time"))

    # Information
    submitter = models.ForeignKey(
        Person,
        related_name="exemption_requests",
        on_delete=models.CASCADE,
        verbose_name=_("Submitter"),
        blank=True,
        null=True,
    )
    description = models.TextField()
    status = models.IntegerField(
        default=0, choices=status_choices, verbose_name=_("Status")
    )

    def mark_as_in_process_2(self):
        """Mark this request as in process 2."""
        self.status = 1
        self.save()

    def approve(self, request):
        """Mark this request as approved."""
        self.status = 2
        self.save()

        notification = Notification(
            sender="Fritak",
            recipient=self.submitter,
            title=_("Your request for an exemption from teaching was approved"),
            description=_(
                "Your request for an exemption from teaching from {}, {} "
                "to {}, {} was approved by the school management.".format(
                    formats.date_format(self.from_date),
                    formats.time_format(self.from_time),
                    formats.date_format(self.to_date),
                    formats.time_format(self.to_time),
                )
            ),
            link=request.build_absolute_uri(reverse("fritak_index")),
        )
        notification.save()

    def reject(self, request):
        """Mark this request as rejected."""
        self.status = 3
        self.save()

        notification = Notification(
            sender="Fritak",
            recipient=self.submitter,
            title=_("Your request for an exemption from teaching was rejected"),
            description=_(
                "Your request for an exemption from teaching from {}, {}  "
                "to {}, {} was rejected by the school management.".format(
                    formats.date_format(self.from_date),
                    formats.time_format(self.from_time),
                    formats.date_format(self.to_date),
                    formats.time_format(self.to_time),
                )
            ),
            link=request.build_absolute_uri(reverse("fritak_index")),
        )
        notification.save()

    def get_status(self):
        return status_list[self.status]

    def __str__(self):
        return self.description

    class Meta:
        permissions = (
            ("check1_exemptionrequest", _("First check of exemption request")),
            ("check2_exemptionrequest", _("Second check of exemption request")),
        )

        verbose_name = _("Exemption request")
        verbose_name_plural = _("Exemption requests")
