import click

from mlfoundry import get_client


@click.group(help="download model or artifacts")
def download():
    ...


@download.command(short_help="Download logged model")
@click.option(
    "--run_fqn",
    required=True,
    type=str,
    help="fqn of the run",
)
@click.option(
    "--path",
    type=click.Path(file_okay=False, dir_okay=True, exists=False),
    required=True,
    help="path where the model will be downloaded",
)
@click.option(
    "--step",
    required=False,
    type=int,
    help="step for which you want to download the model, returns the latest (one logged with the largest step) logged model",
    default=None,
)
def model(run_fqn: str, path: str, step: int):
    """
    Download the logged model for a run.\n
    """
    client = get_client()
    run = client.get_run_by_fqn(run_fqn)
    run.download_model(dest_path=path, step=step)
