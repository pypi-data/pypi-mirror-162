"""
This is CLI for ``nbox``, it is meant to be as simple to use as possible.

..code-block::

  nbx
  ├── tunnel
  ├── open
  ├── compile
  ├── get
  ├── jobs
  │   [staticmethods]
  │   ├── new
  │   ├── status
  │   [initialisation]
  │       ├── id
  │       └── workspace_id
  │   ├── change_schedule
  │   ├──logs
  │   ├──delete
  │   ├──refresh
  │   ├──trigger
  │   ├──pause
  │   └──resume
  └── build (Instance)
      [staticmethods]
      ├── new
      ├── status
      [initialisation]
          ├── i
          ├── workspace_id
          └── cs_endpoint
      ├── refresh
      ├── start
      ├── stop
      ├── delete
      ├── run_py
      └── __call__

"""

import os
import sys
import fire
from json import dumps

import nimblebox.utils as U
from nimblebox.jobs import Job, Serve
from nimblebox.init import nbox_ws_v1
from nimblebox.auth import init_secret
from nimblebox.instance import Instance
from nimblebox.sub_utils.ssh import tunnel
from nimblebox.framework.autogen import compile
from nimblebox.version import __version__ as V

logger = U.get_logger()

def open_home():
  """Open current NBX platform"""
  from .auth import secret
  import webbrowser
  webbrowser.open(secret.get("nbx_url"))


def get(api_end: str, **kwargs):
  """Get any command 

  Args:
    api_end (str): something like '/v1/api'
  """
  api_end = api_end.strip("/")
  if nbox_ws_v1 == None:
    raise RuntimeError("Not connected to NimbleBox.ai webserver")
  out = nbox_ws_v1
  for k in api_end.split("/"):
    out = getattr(out, k)
  res = out(_method = "get", **kwargs)
  sys.stdout.write(dumps(res))
  sys.stdout.flush()

def login():
  fp = U.join(U.env.NBOX_HOME_DIR(), "secrets.json")
  os.remove(fp)
  init_secret()

def version():
  logger.info("NimbleBox.ai Client Library")
  logger.info(f"    nbox version: {V}")


def main():
  fire.Fire({
    "build"   : Instance,
    "compile" : compile,
    "get"     : get,
    "jobs"    : Job,
    "login"   : login,
    "open"    : open_home,
    "serve"   : Serve,
    "tunnel"  : tunnel,
    "version" : version,
  })

if __name__ == "__main__":
  main()
