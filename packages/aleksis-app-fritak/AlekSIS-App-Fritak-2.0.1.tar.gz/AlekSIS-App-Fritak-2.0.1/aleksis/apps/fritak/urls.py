from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="fritak_index"),
    path("apply_for/", views.apply_for, name="fritak_apply_for"),
    path("details/<int:id_>/", views.details, name="fritak_details"),
    path("edit/<int:id_>/", views.edit, name="fritak_edit"),
    path("applied_for/", views.applied_for, name="fritak_applied_for"),
    path("check1/", views.check1, name="fritak_check1"),
    path("check2/", views.check2, name="fritak_check2"),
    path("archive/", views.archive, name="fritak_archive"),
    path(
        "archive/print/", views.archive, {"is_print": True}, name="fritak_print_archive"
    ),
]
