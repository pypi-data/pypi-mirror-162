import os
import json
from pathlib import Path

from traitlets import Unicode
from traitlets.config import Configurable

from .handlers import setup_handlers
from ._version import __version__

HERE = Path(__file__).parent.resolve()


with (HERE / "labextension" / "package.json").open() as fid:
    data = json.load(fid)


def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": data["name"]
    }]


def _jupyter_server_extension_points():
    return [{
      "module": "skillsnetwork-authoring-extension"
    }]


class SkillsNetworkAuthoringExtension(Configurable):
  """
  Configuration options for skillsnetwork_authoring_extension
  """
  atlas_base_url = Unicode(
        default_value=os.environ.get("ATLAS_BASE_URL", "https://author.skills.network/atlas"),
        config=True,
        help="The base URL for the lab file version management service (AKA Atlas)"
  )


def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.
    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    sn_config = SkillsNetworkAuthoringExtension(config=server_app.config)
    server_app.web_app.settings["sn_config"] = sn_config

    url_path = "skillsnetwork-authoring-extension"
    setup_handlers(server_app.web_app, url_path)
    server_app.log.info(
        f"Registered skillsnetwork-authoring-extension at URL path /{url_path}"
    )


# backwards compatibility with jupyterlab 2.0
load_jupyter_server_extension = _load_jupyter_server_extension
_jupyter_server_extension_paths = _jupyter_server_extension_points
