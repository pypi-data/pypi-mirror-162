from datetime import timedelta
from typing import Any, Dict, Optional

import click

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.models.node_type import NodeType
from anyscale.controllers.session_controller import SessionController


log = BlockLogger()


@click.group(
    "logs",
    help="Download log and ray tune result files from Anyscale cluster or job.",
    hidden=True,
)
def log_cli() -> None:
    pass


@log_cli.command(
    name="file", help="Download log files of a cluster or job to BASE_FOLDER."
)
@click.argument("glob", type=str, required=False, default=None, envvar="GLOB")
@click.option("-c", "--cluster-id", type=str, default=None, help="ID of the cluster.")
@click.option("-j", "--job-id", type=str, default=None, help="ID of the job.")
@click.option("-r", "--job-run", type=str, default=None, help="Name of the job run.")
@click.option(
    "-n", "--node-id", type=str, default=None, help="Download logs of a specific node.",
)
@click.option(
    "--worker-only", is_flag=True, help="Download logs of only the worker nodes.",
)
@click.option(
    "--head-only", is_flag=True, help="Download logs of only the head node.",
)
@click.option(
    "--page-size",
    type=int,
    default=None,
    hidden=True,
    help="Results to get in a single API call.",
)
@click.option(
    "--ttl",
    type=int,
    default=None,
    hidden=True,
    help="TTL in seconds for the presigned URL.",
)
@click.option(
    "--parallelism",
    type=int,
    default=None,
    hidden=True,
    help="Number of files to download in parallel at a time.",
)
@click.option(
    "--read-timeout",
    type=int,
    default=None,
    hidden=True,
    help="Read timeout for the http call, while downloading files.",
)
@click.argument(
    "base_folder", type=str, required=True, default="", envvar="BASE_FOLDER"
)
def anyscale_download_log_files(
    glob: Optional[str],
    cluster_id: Optional[str],
    job_id: Optional[str],
    job_run: Optional[str],
    node_id: Optional[str],
    worker_only: bool,
    head_only: bool,
    page_size: Optional[int],
    ttl: Optional[int],
    parallelism: Optional[int],
    read_timeout: Optional[float],
    base_folder: str,
) -> None:
    """Download log files.
    """
    session_controller = SessionController()
    node_type: Optional[NodeType] = None

    if cluster_id is None and job_id is None and job_run is None:
        raise click.ClickException(
            "Atleast one of --cluster-id or --job-id or --job-run must be provided."
        )

    if worker_only and head_only:
        raise click.ClickException("Cannot specify both --worker-only and --head-only.")

    if worker_only:
        node_type = NodeType.WORKER_NODES
    elif head_only:
        node_type = NodeType.HEAD_NODE

    hidden_args: Dict[str, Any] = {"page_size": page_size, "ttl_seconds": ttl}
    if parallelism:
        hidden_args["parallelism"] = parallelism
    if read_timeout:
        hidden_args["read_timeout"] = timedelta(seconds=read_timeout)

    session_controller.download_log_files(
        base_folder=base_folder,
        glob=glob,
        session_id=cluster_id,
        node_id=node_id,
        job_id=job_id,
        job_run=job_run,
        node_type=node_type,
        **hidden_args
    )


@log_cli.command(
    name="results",
    help="Download ray tune result files of a cluster or job to BASE_FOLDER.",
)
@click.option("-c", "--cluster-id", type=str, default=None, help="ID of the cluster.")
@click.option("-j", "--job-id", type=str, default=None, help="ID of the job.")
@click.option("-r", "--job-run", type=str, default=None, help="Name of the job run.")
@click.option(
    "--parallelism",
    type=int,
    default=None,
    hidden=True,
    help="Number of files to download in parallel at a time.",
)
@click.option(
    "--read-timeout",
    type=int,
    default=None,
    hidden=True,
    help="Read timeout for the http call, while downloading files.",
)
@click.argument(
    "base_folder", type=str, required=True, default="", envvar="BASE_FOLDER"
)
def anyscale_download_ray_result_files(
    cluster_id: Optional[str],
    job_id: Optional[str],
    job_run: Optional[str],
    parallelism: Optional[int],
    read_timeout: Optional[float],
    base_folder: str,
) -> None:
    """Download ray tune result files.
    """
    session_controller = SessionController()

    if cluster_id is None and job_id is None and job_run is None:
        raise click.ClickException(
            "Atleast one of --cluster-id or --job-id or --job-run must be provided."
        )

    hidden_args: Dict[str, Any] = {}
    if parallelism:
        hidden_args["parallelism"] = parallelism
    if read_timeout:
        hidden_args["read_timeout"] = timedelta(seconds=read_timeout)

    session_controller.download_ray_result_files(
        base_folder=base_folder,
        session_id=cluster_id,
        job_id=job_id,
        job_run=job_run,
        **hidden_args
    )
