from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import formats
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from guardian.shortcuts import assign_perm, get_objects_for_user
from rules.contrib.views import permission_required

from aleksis.core.models import Activity
from aleksis.core.util import messages
from aleksis.core.util.core_helpers import objectgetter_optional
from aleksis.core.util.pdf import render_pdf

from .filters import ExemptionFilter
from .forms import ApplyForExemptionForm
from .models import ExemptionRequest


@permission_required("fritak.view_index")
def index(request):
    if "id_" in request.POST and "delete" in request.POST:
        exemption_id = request.POST["id_"]
        exemption_request = ExemptionRequest.objects.get(id=exemption_id)
        if not request.user.has_perm(
            "fritak.delete_exemptionrequest", exemption_request
        ):
            raise PermissionDenied
        from_date = formats.date_format(exemption_request.from_date)
        to_date = formats.date_format(exemption_request.to_date)
        exemption_request.delete()
        a = Activity(
            user=request.user.person,
            title=_("Request for exemption from teaching deleted"),
            description=_(
                "You have deleted your request for class exemption"
                + "for the period from {} to {}.".format(from_date, to_date)
            ),
            app="Fritak",
        )
        a.save()
        messages.success(request, _("Your request was successfully deleted."))

    exemption_requests = ExemptionRequest.objects.filter(
        submitter=request.user.person
    ).order_by("-from_date")[:100]

    context = {
        "exemption_requests": exemption_requests,
    }
    return render(request, "fritak/index.html", context)


@permission_required("fritak.view_details", fn=objectgetter_optional(ExemptionRequest))
def details(request, id_):
    exemption_request = get_object_or_404(ExemptionRequest, id=id_)
    context = {"exemption_request": exemption_request}
    return render(request, "fritak/details.html", context)


@never_cache
@permission_required("fritak.apply_exemptionrequest")
def apply_for(request):
    if request.method == "POST":
        form = ApplyForExemptionForm(request.POST)

        if form.is_valid():
            from_date = form.cleaned_data["from_date"]
            from_time = form.cleaned_data["from_time"]
            to_date = form.cleaned_data["to_date"]
            to_time = form.cleaned_data["to_time"]
            description = form.cleaned_data["description"]

            exemption_request = ExemptionRequest(
                from_date=from_date,
                from_time=from_time,
                to_date=to_date,
                to_time=to_time,
                description=description,
                submitter=request.user.person,
            )
            exemption_request.save()
            assign_perm("fritak.view_exemptionrequest", request.user, exemption_request)
            assign_perm(
                "fritak.change_exemptionrequest", request.user, exemption_request
            )
            assign_perm(
                "fritak.delete_exemptionrequest", request.user, exemption_request
            )
            from_date = formats.date_format(from_date)
            to_date = formats.date_format(to_date)

            a = Activity(
                user=request.user.person,
                title=_("Application for exemption from teaching submitted"),
                description=_(
                    "You have applied for an exemption from teaching "
                    + "for the period from {} to {}.".format(from_date, to_date)
                ),
                app="Fritak",
            )
            a.save()
            return redirect("fritak_applied_for")
    else:
        form = ApplyForExemptionForm()

    return render(request, "fritak/apply_for.html", {"form": form})


@never_cache
@permission_required(
    "fritak.edit_exemptionrequest", fn=objectgetter_optional(ExemptionRequest)
)
def edit(request, id_):
    exemption_request = get_object_or_404(ExemptionRequest, id=id_)

    if request.method == "POST":
        form = ApplyForExemptionForm(request.POST, instance=exemption_request)
        if form.is_valid():
            form.save()
            from_date = formats.date_format(exemption_request.from_date)
            to_date = formats.date_format(exemption_request.to_date)
            a = Activity(
                user=request.user.person,
                title=_("Application for exemption from teaching changed"),
                description=_(
                    "You have processed your request for a teaching leave "
                    + "for the period from {} to {}.".format(from_date, to_date)
                ),
                app="Fritak",
            )
            a.save()
            messages.success(request, _("Your request was successfully updated."))
            return redirect("fritak_index")
    else:
        form = ApplyForExemptionForm(instance=exemption_request)

    context = {"form": form}
    return render(request, "fritak/edit.html", context)


@never_cache
@permission_required("fritak.apply_exemptionrequest")
def applied_for(request):
    context = {}

    return render(request, "fritak/applied_for.html", context)


@never_cache
@permission_required("fritak.check1_exemptionrequest")
def check1(request):
    if request.method == "POST":
        if "id" in request.POST:
            exemption_id = request.POST["id"]
            exemption_request = ExemptionRequest.objects.get(id=exemption_id)
            if "approve" in request.POST:
                exemption_request.mark_as_in_process_2()
            elif "reject" in request.POST:
                exemption_request.reject(request)

    exemption_requests = ExemptionRequest.objects.filter(status=0).order_by("from_date")
    return render(
        request, "fritak/check.html", {"exemption_requests": exemption_requests}
    )


@never_cache
@permission_required("fritak.check2_exemptionrequest")
def check2(request):
    if request.method == "POST":
        if "id" in request.POST:
            exemption_id = request.POST["id"]
            exemption_request = ExemptionRequest.objects.get(id=exemption_id)
            if "approve" in request.POST:
                exemption_request.approve(request)
            elif "reject" in request.POST:
                exemption_request.reject(request)

    exemption_requests = ExemptionRequest.objects.filter(status=1).order_by("from_date")
    return render(
        request, "fritak/check.html", {"exemption_requests": exemption_requests}
    )


@permission_required("fritak.view_archive")
def archive(request, is_print: bool = False):
    if not is_print:
        exemption_list = ExemptionRequest.objects.filter(
            Q(status__exact=2) | Q(status__exact=3)
        ).order_by("-from_date")
    else:
        exemption_list = ExemptionRequest.objects.all().order_by("from_date")
    exemption_list = get_objects_for_user(
        request.user, "fritak.view_exemptionrequest", exemption_list
    )

    if not is_print:
        exemption_filter = ExemptionFilter(request.GET, queryset=exemption_list)
        return render(request, "fritak/archive.html", {"filter": exemption_filter})
    else:
        return render_pdf(
            request, "fritak/archive_print.html", {"exemption_list": exemption_list}
        )
