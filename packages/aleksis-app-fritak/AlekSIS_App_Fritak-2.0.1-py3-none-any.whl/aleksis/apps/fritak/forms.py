from datetime import datetime

from django import forms
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import OperationalError, ProgrammingError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from material import Fieldset, Layout, Row

from .models import ExemptionRequest

period_choices = [("", "")]

chronos_installed = apps.is_installed("aleksis.apps.chronos")
time_periods = []
if chronos_installed:
    from aleksis.apps.chronos.models import TimePeriod

    try:
        time_periods = (
            TimePeriod.objects.filter(weekday=TimePeriod.weekday_min)
            .for_current_or_all()
            .values("period", "time_start", "time_end")
            .distinct()
        )

        period_choices += [
            (period, f"{period}.")
            for period in time_periods.values_list("period", flat=True)
        ]
    except (ProgrammingError, OperationalError):
        pass


def get_time_min():

    if chronos_installed:
        return TimePeriod.time_min
    return None


def get_time_max():
    if chronos_installed:
        return TimePeriod.time_max
    return None


class ApplyForExemptionForm(forms.ModelForm):
    from_date = forms.DateField(label=_("Date"))
    from_lesson = forms.ChoiceField(
        label=_("Lesson"),
        choices=period_choices,
        required=False,
    )
    from_time = forms.TimeField(
        label=_("Time"),
        initial=get_time_min,
        required=False,
    )

    to_date = forms.DateField(label=_("Date"))
    to_lesson = forms.ChoiceField(
        label=_("Lesson"),
        choices=period_choices,
        required=False,
    )
    to_time = forms.TimeField(
        label=_("Time"),
        initial=get_time_max,
        required=False,
    )

    description = forms.CharField(label=_("Please give reasons for your request."))

    layout = Layout(
        Fieldset(
            _("From"),
            Row("from_date", "from_lesson", "from_time"),
        ),
        Fieldset(
            _("To"),
            Row("to_date", "to_lesson", "to_time"),
        ),
        Fieldset(_("Reason / Project"), "description"),
    )

    class Meta:
        model = ExemptionRequest
        fields = ("id", "from_date", "from_time", "to_date", "to_time", "description")

    def clean(self):
        cleaned_data = super().clean()

        cleaned_data = self.clean_from_to_date()

        return cleaned_data

    def clean_from_to_date(self):
        # not related to a form field, just to clean datetime values

        from_date = self.cleaned_data.get("from_date")
        from_time = self.cleaned_data.get("from_time")
        from_lesson = self.cleaned_data.get("from_lesson")

        to_date = self.cleaned_data.get("to_date")
        to_time = self.cleaned_data.get("to_time")
        to_lesson = self.cleaned_data.get("to_lesson")

        # Check from lesson or from time
        if (from_time and from_lesson) or (not from_time and not from_lesson):
            raise ValidationError(
                _("Please select either a from lesson or a from time.")
            )
        elif not from_time and from_lesson:
            from_time = time_periods.filter(period=from_lesson).first()["time_start"]

        # Check to lesson or to time
        if (to_time and to_lesson) or (not to_time and not to_lesson):
            raise ValidationError(_("Please select either a to lesson or a to time."))
        elif not to_time and to_lesson:
            to_time = time_periods.filter(period=to_lesson).first()["time_end"]

        self.cleaned_data["from_time"] = from_time
        self.cleaned_data["to_time"] = to_time

        if from_date and from_time and to_date and to_time:
            from_datetime = timezone.datetime.combine(from_date, from_time)
            to_datetime = timezone.datetime.combine(to_date, to_time)

            if (from_datetime < datetime.now()) or (to_datetime < datetime.now()):
                raise ValidationError(
                    _(
                        "The exemption cannot be carried out for days already past (date error)."
                    )
                )
            elif from_datetime > to_datetime:
                raise ValidationError(_("The from date is after the to date."))

        return self.cleaned_data

    def clean_description(self):
        data = self.cleaned_data["description"]

        if len(data) < 10:
            raise ValidationError(
                _("Please tell us a little bit more about your exemption.")
            )

        return data
