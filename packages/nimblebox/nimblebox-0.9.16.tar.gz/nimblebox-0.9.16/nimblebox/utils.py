"""
Utility objects and functions.

This has a couple of cool things:

#. ``get_logger``: a master logger for nbox, this can be modified to log through anything
#. ``isthere``: a decorator that checks if a package is installed, if not it raises an error\
  It is more complicated than it needs to be because it is seedling for a way to package\
  functions and code together so that it can be used in a more dynamic way.
#. ``get_files_in_folder``: a function that returns all files in a folder with a certain extension
#. ``fetch``: a function that fetches a url and caches it in ``tempdir`` for faster loading
#. ``get_random_name``: a function that returns a random name, if ``True`` is passed returns\
  an ``uuid4()`` for truly random names :)
#. ``hash_``: a function that returns a hash of any python object, string is accurate, others\
  might be anything, but atleast it returns something.
#. ``folder/join``: to be used in pair, ``join(folder(__file__), "server_temp.jinja")`` means\
  relative path "../other.py". Scattered throughout the codebase, the super generic name will\
  bite me.
#. ``to_pickle/from_pickle``: to be used in pair, ``to_pickle(obj, "path")`` and ``from_pickle("path")``\
  to save and load python objects to disk.
#. ``DBase``: सस्ता-protobuf (cheap protobuf), can be nested and ``get_dict`` will get for all\
  children
#. ``PoolBranch``: Or how to use multiprocessing, but blocked so you don't have to give a shit\
  about it.
"""

############################################################
# This file is d0 meaning that this has no dependencies!
# Do not import anything from rest of nbox here!
############################################################

# this file has bunch of functions that are used everywhere

import os
import io
import sys
import dill
import logging
import hashlib
import requests
import tempfile
import traceback
import randomname
from uuid import uuid4
from functools import partial
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

class env:
  """
  Single namespace for all environment variables.
  
  #. ``NBOX_LOG_LEVEL``: Logging level for ``nbox``, set ``NBOX_LOG_LEVEL=info|debug|warning"
  #. ``NBOX_JSON_LOG``: Whether to print json-logs, set ``NBOX_JSON_LOG=1``
  #. ``NBOX_JOB_FOLDER``: Folder path for the job, set ``NBOX_JOB_FOLDER=/tmp/nbox/jobs"``
  #. ``NBOX_NO_AUTH``: If set ``secrets = None``, this will break any API request and is good only for local testing
  #. ``NBOX_SSH_NO_HOST_CHECKING``: If set, ``ssh`` will not check for host key
  #. ``NBOX_HOME_DIR``: By default ~/.nbx folder
  #. ``NBOX_USER_TOKEN``: User token for NimbleBox.ai from <app.nimblebox.ai/secrets>_
  """
  NBOX_LOG_LEVEL = lambda x: os.getenv("NBOX_LOG_LEVEL", x)
  NBOX_JSON_LOG = lambda x: os.getenv("NBOX_JSON_LOG", x)
  NBOX_JOB_FOLDER = lambda x: os.getenv("NBOX_JOB_FOLDER", x)
  NBOX_NO_AUTH = lambda x: os.getenv("NBOX_NO_AUTH", x)
  NBOX_SSH_NO_HOST_CHECKING = lambda x: os.getenv("NBOX_SSH_NO_HOST_CHECKING", x)
  NBOX_HOME_DIR = lambda : os.environ.get("NBOX_HOME_DIR", os.path.join(os.path.expanduser("~"), ".nbx"))
  NBOX_USER_TOKEN = lambda x: os.getenv("NBOX_USER_TOKEN", x)
  NBOX_NO_LOAD_GRPC = lambda: os.getenv("NBOX_NO_LOAD_GRPC", False)

logger = None

def get_logger():
  # add some handling so files can use functional way of getting logger
  global logger
  if logger is not None:
    return logger

  logger = logging.getLogger("utils")
  lvl = env.NBOX_LOG_LEVEL("info").upper()
  logger.setLevel(getattr(logging, lvl))

  if env.NBOX_JSON_LOG(False):
    logHandler = logging.StreamHandler()
    logHandler.setFormatter(jsonlogger.JsonFormatter(
      '%(timestamp)s %(levelname)s %(message)s ',
      timestamp=True
    ))
    logger.addHandler(logHandler)
  else:
    logHandler = logging.StreamHandler()
    logHandler.setFormatter(logging.Formatter(
      '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
      datefmt = "%Y-%m-%dT%H:%M:%S%z"
    ))
    logger.addHandler(logHandler)

  return logger

logger = get_logger() # package wide logger


class FileLogger:
  def __init__(self, filepath):
    self.filepath = filepath
    self.f = open(filepath, "a+")

    self.debug = partial(self.log, level="debug",)
    self.info = partial(self.log, level="info",)
    self.warning = partial(self.log, level="warning",)
    self.error = partial(self.log, level="error",)
    self.critical = partial(self.log, level="critical",)

  def log(self, message, level):
    self.f.write(f"[{datetime.now(timezone.utc).isoformat()}] {level}: {message}\n")
    self.f.flush()


def log_and_exit(msg, *args, **kwargs):
  # convinience function to avoid tracebacks
  logger.error(msg, *args, **kwargs)
  sys.exit(1)

# lazy_loading/

def isthere(*packages, soft = True):
  """Checks all the packages

  Args:
      soft (bool, optional): If ``False`` raises ``ImportError``. Defaults to True.
  """
  def wrapper(fn):
    _fn_ = fn
    def _fn(*args, **kwargs):
      # since we are lazy evaluating this thing, we are checking when the function
      # is actually called. This allows checks not to happen during __init__.
      for package in packages:
        # split the package name to get version number as well, not all will have package
        # version so continue those that have a version
        package = package.split("==")
        if len(package) == 1:
          package_name, package_version = package[0], None
        else:
          package_name, package_version = package
        if package_name in sys.modules:
          # trying to install these using pip will cause issues, so avoid that
          continue

        try:
          module = __import__(package_name)
          if hasattr(module, "__version__") and package_version:
            if module.__version__ != package_version:
              raise ImportError(f"{package_name} version mismatch")
        except ImportError:
          if not soft:
            raise ImportError(f"{package} is not installed, but is required by {fn}")
          # raise a warning, let the modulenotfound exception bubble up
          logger.warning(
            f"{package} is not installed, but is required by {fn.__module__}, some functionality may not work"
          )
      return _fn_(*args, **kwargs)
    return _fn
  return wrapper


# /lazy_loading

# path/

def get_files_in_folder(folder, ext = ["*"]):
  """Get files with ``ext`` in ``folder``"""
  # this method is faster than glob
  import os
  all_paths = []
  _all = "*" in ext # wildcard means everything so speed up

  folder_abs = os.path.abspath(folder)
  for root,_,files in os.walk(folder_abs):
    if _all:
      all_paths.extend([join(root, f) for f in files])
      continue

    for f in files:
      for e in ext:
        if f.endswith(e):
          all_paths.append(os.path.join(root,f))
  return all_paths

def fetch(url, force = False):
  """Fetch and cache a url for faster loading, ``force`` re-downloads"""
  fp = join(tempfile.gettempdir(), hash_(url))
  if os.path.isfile(fp) and os.stat(fp).st_size > 0 and not force:
    with open(fp, "rb") as f:
      dat = f.read()
  else:
    dat = requests.get(url).content
    with open(fp + ".tmp", "wb") as f:
      f.write(dat)
    os.rename(fp + ".tmp", fp)
  return dat

def folder(x):
  """get the folder of this file path"""
  return os.path.split(os.path.abspath(x))[0]

def join(x, *args):
  """convienience function for os.path.join"""
  return os.path.join(x, *args)

def to_pickle(obj, path):
  with open(path, "wb") as f:
    dill.dump(obj, f)

def from_pickle(path):
  with open(path, "rb") as f:
    return dill.load(f)


# /path

# misc/

def get_random_name(uuid = False):
  """Get a random name, if ``uuid`` is ``True``, return a uuid4"""
  if uuid:
    return str(uuid4())
  return randomname.generate()

def hash_(item, fn="md5"):
  """Hash sting of any item"""
  return getattr(hashlib, fn)(str(item).encode("utf-8")).hexdigest()


def log_traceback():
  f = io.StringIO("")
  traceback.print_exception(*sys.exc_info(), file = f)
  f.seek(0)
  for _l in f.readlines():
    logger.error(_l.rstrip())

# /misc

# datastore/

class DBase:
  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      setattr(self, k, v)

  def get(self, k, v = None):
    return getattr(self, k, v)
  
  def get_dict(self):
    data = {}
    for k in self.__slots__:
      _obj = getattr(self, k, None)
      if _obj == None:
        continue
      if isinstance(_obj, DBase):
        data[k] = _obj.get_dict()
      elif _obj != None and isinstance(_obj, (list, tuple)) and len(_obj) and isinstance(_obj[0], DBase):
        data[k] = [_obj.get_dict() for _obj in _obj]
      else:
        data[k] = _obj
    return data

  def __repr__(self):
    return str(self.get_dict())

# /datastore

# model/

@isthere("PIL", soft = False)
def get_image(file_path_or_url):
  from PIL import Image
  if os.path.exists(file_path_or_url):
    return Image.open(file_path_or_url)
  else:
    return Image.open(io.BytesIO(fetch(file_path_or_url)))

def convert_to_list(x):
  # recursively convert tensors -> list
  import torch
  import numpy as np

  x = x.outputs.detach()

  if isinstance(x, list):
    return x
  if isinstance(x, dict):
    return {k: convert_to_list(v) for k, v in x.items()}
  elif isinstance(x, (torch.Tensor, np.ndarray)):
    x = np.nan_to_num(x, -1.42069)
    return x.tolist()
  else:
    raise Exception("Unknown type: {}".format(type(x)))

# /model


################################################################################
# Parallel
# ========
# There already are many multiprocessing libraries for thread, core, pod, cluster
# but thee classes below are inspired by https://en.wikipedia.org/wiki/Collective_operation
#
# And that is why they are blocking classes, ie. it won't stop till all the tasks
# are completed. For reference please open the link above which has diagrams, there
# nodes can just be threads/cores/... Here is description for each of them:
#
# - Pool: apply same functions on different inputs
# - Branch: apply different functions on different inputs
################################################################################

# pool/

class PoolBranch:
  def __init__(self, mode = "thread", max_workers = 2, _name: str = None):
    """Threading is hard, your brain is not wired to handle parallelism. You are a blocking
    python program. So a blocking function for you. There are some conditions:


    Usage:

    .. code-block:: python

      # define some functions

      def add_zero(x):  return x + 0
      def add_one(x):   return x + 1
      def add_ten(x):   return x + 10
      def add_fifty(x): return x + 50

      all_fn = [add_zero, add_one, add_ten, add_fifty]

      # define some arguments
      args = [(1,), (2,), (3,), (4,),]

      # branching is applying different functions on different inputs
      branch = PoolBranch("thread")
      out = branch(all_fn, *args)

      # pooling is applying same functions on different inputs
      pool = PoolBranch("thread")
      out = pool(add_zero, *args)

    When using ``mode = "process"`` write your code in a function and ensure that the
    function is called from ``__main__ == "__name__"``. From the documentation of ``concurrent.futures``:

      The __main__ module must be importable by worker subprocesses. This means that
      ``ProcessPoolExecutor`` will not work in the interactive interpreter.

    - `StackOverflow <https://stackoverflow.com/questions/27932987/multiprocessing-package-in-interactive-python>`_
    - `Another <https://stackoverflow.com/questions/24466804/multiprocessing-breaks-in-interactive-mode>`_

    .. code-block:: python

      def multiprocess():
        print("MultiProcessing")

        branch = PoolBranch("process")
        out = branch(all_fn, *args)

        pool = PoolBranch("process")
        out = pool(add_zero, *args)

      if __name__ == "__main__":
        multiprocess()

    Args:
      mode (str, optional): There can be multiple pooling strategies across cores, threads,
        k8s, nbx-instances etc.
      max_workers (int, optional): Numbers of workers to use
    """
    self.mode = mode
    self.item_id = -1 # because +1 later
    self.futures = {}
    self._name = _name or get_random_name(True)

    if mode == "thread":
      self.executor = ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix=self._name
      )
    elif mode == "process":
      self.executor = ProcessPoolExecutor(
        max_workers=max_workers,
      )
    else:
      raise Exception(f"Only 'thread/process' modes are supported")

    logger.debug(f"Starting {mode.upper()}-PoolBranch ({self._name}) with {max_workers} workers")

  def __call__(self, fn, *args):
    """Run any function ``fn`` in parallel, where each argument is a list of arguments to
    pass to ``fn``. Result is returned in the **same order as the input**.

      ..code-block

        if fn is callable:
          thread(fn, a) for a in args -> list of results
        elif fn is list and fn[0] is callable:
          thread(_fn, a) for _fn, a in (fn args) -> list of results
    """
    assert isinstance(args[0], (tuple, list))

    futures = {}
    if isinstance(fn, (list, tuple)) and callable(fn[0]):
      assert len(fn) == len(args), f"Number of functions ({len(fn)}) and arguments ({len(args)}) must be same in branching"
    else:
      assert callable(fn), "fn must be callable in pooling"
      fn = [fn for _ in range(len(args))] # convinience

    self.item_id += len(futures)
    results = {}

    if self.mode in ("thread", "process"):
      for i, (_fn, x) in enumerate(zip(fn, args)):
        futures[self.executor.submit(_fn, *x)] = i # insertion index
      for future in as_completed(futures):
        try:
          result = future.result()
          results[futures[future]] = result # update that index
        except Exception as e:
          logger.error(f"{self.mode} error: {e}")
          raise e

      res = [results[x] for x in range(len(results))]

    return res

# /pool
