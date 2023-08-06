from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

from .models import ExemptionRequest


# prevent to show exemption details from foreign users
def check_own_exemption_verification(user):
    return ExemptionRequest.objects.all().filter(submitter=user.person)


def check_own_exemption(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Check that the user only gets his own exemption.

    Redirecting to the dashboard if necessary.
    """
    actual_decorator = user_passes_test(
        check_own_exemption_verification,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )

    if function:
        return actual_decorator(function)
    return actual_decorator
