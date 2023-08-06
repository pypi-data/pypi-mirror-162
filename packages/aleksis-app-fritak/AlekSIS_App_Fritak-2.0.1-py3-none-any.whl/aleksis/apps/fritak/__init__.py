import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("AlekSIS-App-Fritak").version
except Exception:
    __version__ = "unknown"

default_app_config = "aleksis.apps.fritak.apps.FritakConfig"
