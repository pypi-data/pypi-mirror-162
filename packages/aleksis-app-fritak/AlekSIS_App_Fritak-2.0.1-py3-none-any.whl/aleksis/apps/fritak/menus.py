from django.utils.translation import ugettext_lazy as _

MENUS = {
    "NAV_MENU_CORE": [
        {
            "name": _("Requests for exemption"),
            "url": "#",
            "svg_icon": "mdi:clipboard-account-outline",
            "root": True,
            "validators": [
                ("menu_generator.validators.user_has_permission", "fritak.view_menu"),
            ],
            "submenu": [
                {
                    "name": _("My requests"),
                    "url": "fritak_index",
                    "svg_icon": "mdi:account-details-outline",
                    "validators": [
                        (
                            "menu_generator.validators.user_has_permission",
                            "fritak.apply_exemptionrequest",
                        ),
                    ],
                },
                {
                    "name": _("Approve requests 1"),
                    "url": "fritak_check1",
                    "svg_icon": "mdi:check",
                    "validators": [
                        (
                            "menu_generator.validators.user_has_permission",
                            "fritak.check1_exemptionrequest",
                        )
                    ],
                },
                {
                    "name": _("Approve requests 2"),
                    "url": "fritak_check2",
                    "svg_icon": "mdi:check-all",
                    "validators": [
                        (
                            "menu_generator.validators.user_has_permission",
                            "fritak.check2_exemptionrequest",
                        )
                    ],
                },
                {
                    "name": _("Archive"),
                    "url": "fritak_archive",
                    "svg_icon": "mdi:archive-outline",
                    "validators": [
                        (
                            "menu_generator.validators.user_has_permission",
                            "fritak.view_archive",
                        )
                    ],
                },
            ],
        }
    ]
}
