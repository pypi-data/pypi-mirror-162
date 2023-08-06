from aleksis.core.util.apps import AppConfig


class FritakConfig(AppConfig):
    name = "aleksis.apps.fritak"
    verbose_name = "AlekSIS — Fritak (Exemption requests)"

    urls = {
        "Repository": "https://edugit.org/katharineum/AlekSIS-App-Fritak",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2017, 2018, 2019, 2020], "Frank Poetzsch-Heffter", "p-h@katharineum.de"),
        ([2017, 2018, 2019, 2020], "Jonathan Weth", "wethjo@katharineum.de"),
        ([2018, 2019, 2020], "Julian Leucker", "leuckeju@katharineum.de"),
        ([2018, 2019, 2020], "Hangzhi Yu", "yuha@katharineum.de"),
    )
