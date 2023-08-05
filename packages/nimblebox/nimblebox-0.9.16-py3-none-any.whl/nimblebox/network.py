"""
Network functions are gateway between NBX-Services. If you find yourself using this
you might want to reach out to us <research-at-nimblebox-dot-ai>!

But for the curious mind, many of our services work on gRPC and Protobufs. This network.py
manages the quirkyness of our backend and packs multiple steps as one function.
"""

import os
import re
import grpc
import jinja2
import fnmatch
import zipfile
import requests
from tempfile import gettempdir
from datetime import datetime, timezone
from google.protobuf.field_mask_pb2 import FieldMask

import nimblebox.utils as U
from nimblebox.auth import secret
from nimblebox.utils import logger
from nimblebox.version import __version__
from nimblebox.hyperloop.dag_pb2 import DAG
from nimblebox.init import nbox_ws_v1, nbox_grpc_stub
from nimblebox.hyperloop.job_pb2 import NBXAuthInfo, Job as JobProto, Resource
from nimblebox.messages import rpc, write_string_to_file, get_current_timestamp
from nimblebox.jobs import Schedule, _get_job_data, _get_deployment_data, JobInfo
from nimblebox.hyperloop.nbox_ws_pb2 import UploadCodeRequest, CreateJobRequest, UpdateJobRequest


#######################################################################################################################
"""
# Serving

Function related to serving of any model.
"""
#######################################################################################################################


def deploy_serving(
  init_folder: str,
  deployment_id_or_name: str,
  workspace_id: str = None,
  resource: Resource = None,
  wait_for_deployment: bool = False,
  *,
  _unittest = False
):
  """Use the NBX-Deploy Infrastructure"""
  # check if this is a valid folder or not
  if not os.path.exists(init_folder) or not os.path.isdir(init_folder):
    raise ValueError(f"Incorrect project at path: '{init_folder}'! nbox jobs new <name>")

  if resource is not None:
    logger.warning("Resource is coming in the following release!")
  if wait_for_deployment:
    logger.warning("Wait for deployment is coming in the following release!")

  serving_id, serving_name = _get_deployment_data(deployment_id_or_name, workspace_id)
  logger.info(f"Serving name: {serving_name}")
  logger.info(f"Serving ID: {serving_id}")
  model_name = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
  logger.debug(f"Model name: {model_name}")

  # zip init folder
  zip_path = zip_to_nbox_folder(init_folder, serving_id, workspace_id, model_name = model_name)
  _upload_serving_zip(zip_path, workspace_id, serving_id, serving_name, model_name)


def _upload_serving_zip(zip_path, workspace_id, serving_id, serving_name, model_name):
  file_size = os.stat(zip_path).st_size # serving in bytes

  # get bucket URL and upload the data
  stub_all_depl = nbox_ws_v1.workspace.u(workspace_id).deployments
  out = stub_all_depl.u(serving_id).get_upload_url(
    _method = "put",
    convert_args = "",
    deployment_meta = {},
    deployment_name = serving_name,
    deployment_type = "nbox_op", # "nbox" or "ovms2"
    file_size = str(file_size),
    file_type = "nbox",
    model_name = model_name,
    nbox_meta = {},
  )

  model_id = out["fields"]["x-amz-meta-model_id"]
  deployment_id = out["fields"]["x-amz-meta-deployment_id"]
  logger.debug(f"model_id: {model_id}")
  logger.debug(f"deployment_id: {deployment_id}")

  # upload the file to a S3 -> don't raise for status here
  logger.debug("Uploading model to S3 ...")
  r = requests.post(url=out["url"], data=out["fields"], files={"file": (out["fields"]["key"], open(zip_path, "rb"))})
  status = r.status_code == 204
  logger.debug(f"Upload status: {status}")

  # checking if file is successfully uploaded on S3 and tell webserver whether upload is completed or not
  ws_stub_model = stub_all_depl.u(deployment_id).models.u(model_id) # eager create the stub
  ws_stub_model.update(_method = "post", status = status)

  # write out all the commands for this deployment
  logger.info("API will soon be hosted, here's how you can use it:")
  _api = f"Operator.from_serving('{serving_id}', $NBX_TOKEN, '{workspace_id}')"
  _cli = f"python3 -m nbox serve forward --id_or_name '{serving_id}' --workspace_id '{workspace_id}'"
  _curl = f"curl https://api.nimblebox.ai/{serving_id}/forward"
  _webpage = f"{secret.get('nbx_url')}/workspace/{workspace_id}/deploy/{serving_id}"
  logger.info(f" [python] - {_api}")
  logger.info(f"    [CLI] - {_cli} --token $NBX_TOKEN --args")
  logger.info(f"   [curl] - {_curl} -H 'NBX-KEY: $NBX_TOKEN' -H 'w' -d " + "'{}'")
  logger.info(f"   [page] - {_webpage}")


#######################################################################################################################
"""
# Jobs

Function related to batch processing of any model.
"""
#######################################################################################################################


def deploy_job(
  init_folder: str,
  job_id_or_name: str,
  dag: DAG,
  workspace_id: str = None,
  schedule: Schedule = None,
  resource: Resource = None,
  *,
  _unittest = False
) -> None:
  """Upload code for a NBX-Job.

  Args:
    init_folder (str, optional): Name the folder to zip
    job_id_or_name (Union[str, int], optional): Name or ID of the job
    dag (DAG): DAG to upload
    workspace_id (str): Workspace ID to deploy to, if not specified, will use the personal workspace
    schedule (Schedule, optional): If ``None`` will run only once, else will schedule the job
    cache_dir (str, optional): Folder where to put the zipped file, if ``None`` will be ``tempdir``
  Returns:
    Job: Job object
  """
  # check if this is a valid folder or not
  if not os.path.exists(init_folder) or not os.path.isdir(init_folder):
    raise ValueError(f"Incorrect project at path: '{init_folder}'! nbox jobs new <name>")

  job_id, job_name = _get_job_data(job_id_or_name, workspace_id)
  logger.info(f"Job name: {job_name}")
  logger.info(f"Job ID: {job_id}")

  # intialise the console logger
  URL = secret.get("nbx_url")
  logger.debug(f"Schedule: {schedule}")
  logger.debug("-" * 30 + " NBX Jobs " + "-" * 30)
  logger.debug(f"Deploying on URL: {URL}")

  # create the proto for this Operator
  job_proto = JobProto(
    id = job_id,
    name = job_name or U.get_random_name(True).split("-")[0],
    created_at = get_current_timestamp(),
    auth_info = NBXAuthInfo(
      username = secret.get("username"),
      workspace_id = workspace_id,
    ),
    schedule = schedule.get_message() if schedule is not None else None,
    dag = dag,
    resource = Resource(
      cpu = "100m",         # 100mCPU
      memory = "200Mi",     # MiB
      disk_size = "1Gi",    # GiB
    ) if resource == None else resource,
  )
  write_string_to_file(job_proto, U.join(init_folder, "job_proto.pbtxt"))

  if _unittest:
    return job_proto

  # zip the entire init folder to zip
  zip_path = zip_to_nbox_folder(init_folder, job_id, workspace_id)
  _upload_job_zip(zip_path, job_proto)

def _upload_job_zip(zip_path: str, job_proto: JobProto):
  # determine if it's a new Job based on GetJob API
  try:
    j: JobProto = nbox_grpc_stub.GetJob(JobInfo(job = job_proto))
    new_job = j.status == JobProto.Status.NOT_SET
  except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
      new_job = True
    else:
      raise e

  if not new_job:
    # incase an old job exists, we need to update few things with the new information
    from nimblebox.jobs import Job
    logger.debug("Found existing job, checking for update masks")
    old_job_proto = Job(job_proto.id, job_proto.auth_info.workspace_id).job_proto
    paths = []
    if old_job_proto.resource.SerializeToString(deterministic = True) != job_proto.resource.SerializeToString(deterministic = True):
      paths.append("resource")
    if old_job_proto.schedule.cron != job_proto.schedule.cron:
      paths.append("schedule.cron")
    logger.debug(f"Updating fields: {paths}")
    nbox_grpc_stub.UpdateJob(
      UpdateJobRequest(job = job_proto, update_mask = FieldMask(paths=paths)),
    )

  # update the JobProto with file sizes
  job_proto.code.MergeFrom(JobProto.Code(
    size = max(int(os.stat(zip_path).st_size / (1024 ** 2)), 1), # jobs in MiB
    type = JobProto.Code.Type.ZIP,
  ))

  # UploadJobCode is responsible for uploading the code of the job
  response: JobProto = rpc(
    nbox_grpc_stub.UploadJobCode,
    UploadCodeRequest(job = job_proto, auth = job_proto.auth_info),
    f"Failed to upload job: {job_proto.id} | {job_proto.name}"
  )
  job_proto.MergeFrom(response)
  s3_url = job_proto.code.s3_url
  s3_meta = job_proto.code.s3_meta
  logger.debug("Uploading model to S3 ...")
  r = requests.post(url=s3_url, data=s3_meta, files={"file": (s3_meta["key"], open(zip_path, "rb"))})
  try:
    r.raise_for_status()
  except:
    logger.error(f"Failed to upload model: {r.content.decode('utf-8')}")
    return

  # if this is the first time this is being created
  if new_job:
    rpc(nbox_grpc_stub.CreateJob, CreateJobRequest(job = job_proto), f"Failed to create job")

  # write out all the commands for this job
  logger.info("Run is now created, to 'trigger' programatically, use the following commands:")
  _api = f"nbox.Job(id = '{job_proto.id}', workspace_id='{job_proto.auth_info.workspace_id}').trigger()"
  _cli = f"python3 -m nbox jobs --id {job_proto.id} --workspace_id {job_proto.auth_info.workspace_id} trigger"
  _curl = f"curl -X POST {secret.get('nbx_url')}/api/v1/workspace/{job_proto.auth_info.workspace_id}/job/{job_proto.id}/trigger"
  _webpage = f"{secret.get('nbx_url')}/workspace/{job_proto.auth_info.workspace_id}/jobs/{job_proto.id}"
  logger.info(f" [python] - {_api}")
  logger.info(f"    [CLI] - {_cli}")
  logger.info(f"   [curl] - {_curl} -H 'authorization: Bearer $NBX_TOKEN' -H 'Content-Type: application/json' -d " + "'{}'")
  logger.info(f"   [page] - {_webpage}")

  # create a Job object and return so CLI can do interesting things
  from nimblebox.jobs import Job
  return Job(job_proto.id, job_proto.auth_info.workspace_id)


#######################################################################################################################
"""
# Common

Function related to both NBX-Serving and NBX-Jobs
"""
#######################################################################################################################

def zip_to_nbox_folder(init_folder, id, workspace_id, **jinja_kwargs):
  # zip all the files folder
  all_f = U.get_files_in_folder(init_folder)

  # find a .nboxignore file and ignore items in it
  to_ignore_pat = []
  to_ignore_folder = []
  for f in all_f:
    if f.split("/")[-1] == ".nboxignore":
      with open(f, "r") as _f:
        for pat in _f:
          pat = pat.strip()
          if pat.endswith("/"):
            to_ignore_folder.append(pat)
          else:
            to_ignore_pat.append(pat)
      break

  # two different lists for convinience
  to_remove = []
  for ignore in to_ignore_pat:
    x = fnmatch.filter(all_f, ignore)
    to_remove.extend(x)
  to_remove_folder = []
  for ignore in to_ignore_folder:
    for f in all_f:
      if re.search(ignore, f):
        to_remove_folder.append(f)
  to_remove += to_remove_folder

  all_f = [x for x in all_f if x not in to_remove]
  logger.info(f"Will zip {len(all_f)} files")

  # zip all the files folder
  zip_path = U.join(gettempdir(), f"nbxjd_{id}@{workspace_id}.nbox")
  logger.info(f"Packing project to '{zip_path}'")
  with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    abspath_init_folder = os.path.abspath(init_folder)
    for f in all_f:
      arcname = f[len(abspath_init_folder)+1:]
      logger.debug(f"Zipping {f} => {arcname}")
      zip_file.write(f, arcname = arcname)

    if not "exe.py" in zip_file.namelist():
      logger.debug("exe.py already in zip")

      # get a timestamp like this: Monday W34 [UTC 12 April, 2022 - 12:00:00]
      _ct = datetime.now(timezone.utc)
      _day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][_ct.weekday()]
      created_time = f"{_day} W{_ct.isocalendar()[1]} [ UTC {_ct.strftime('%d %b, %Y - %H:%M:%S')} ]"

      # create the exe.py file
      exe_jinja_path = U.join(U.folder(__file__), "assets", "exe.jinja")
      exe_path = U.join(gettempdir(), "exe.py")
      logger.debug(f"Writing exe to: {exe_path}")
      with open(exe_jinja_path, "r") as f, open(exe_path, "w") as f2:
        f2.write(jinja2.Template(f.read()).render({
          "created_time": created_time,
          "nbox_version": __version__,
          **jinja_kwargs
        }))
      zip_file.write(exe_path, arcname = "exe.py")

  return zip_path
