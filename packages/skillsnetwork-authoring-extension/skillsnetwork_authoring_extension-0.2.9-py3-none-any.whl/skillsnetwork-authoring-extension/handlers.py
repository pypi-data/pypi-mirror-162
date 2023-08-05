import json
import os

import tornado
from notebook.base.handlers import IPythonHandler
from notebook.utils import url_path_join


class AppHandler(IPythonHandler):
  """Thin wrapper around the IPython handler which injects common properties."""
  @property
  def config(self):
      return self.settings["sn_config"]

class ConfigurationEndpointHandler(AppHandler):
  """
  Route handler for the /skillsnetwork-authoring-extension/config endpoint.

  A single endpoint that returns the Atlas base URL.
  """
  def get(self) -> None:
    print('test', type(self.config))
    self.finish({"ATLAS_BASE_URL": self.config.atlas_base_url})

class AtlasGatewayEndpointHandler(AppHandler):
  """Route handler for the /skillsnetwork-authoring-extension/gateway endpoint.

  This endpoint is a GET request that takes in a token URL parameter,
  saves it in the session (so it accessibly by JupyterLab), and then
  redirects to the JupyterLab instance.
  """
  @tornado.web.authenticated
  def get(self) -> None:
    token = self.get_argument('token', default=None)
    if token is None:
      # TODO: Raise an error here or return some error message...
      self.finish('Token is a required URL parameter!')
    else:
      self.log.info(f'Received ATLAS token: {token}')
      # Set cookie that contains the ATLAS token
      self.set_cookie('atlas_token', token)
      # Redirect to index
      self.redirect('/')


def setup_handlers(web_app, url_path: str) -> None:
  """Setup handlers in the jupyter server web app.

  Args:
    - web_app: Jupyter server web application instance to add handlers to.
    - url_path: Root url path for handlers.
  """
  host_pattern = ".*$"
  base_url = web_app.settings["base_url"]

  # Prepend the base_url so that it works in a JupyterHub setting
  handler_url_path = url_path_join(base_url, url_path)
  handlers = [
    (url_path_join(handler_url_path, "gateway"), AtlasGatewayEndpointHandler),
    (url_path_join(handler_url_path, "config"), ConfigurationEndpointHandler)
  ]
  web_app.add_handlers(host_pattern, handlers)
