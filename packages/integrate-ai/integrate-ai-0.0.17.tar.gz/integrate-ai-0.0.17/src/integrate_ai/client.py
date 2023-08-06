import typer
import logging
import os
import rich
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn
from integrate_ai.utils.docker_client import DockerClient
from pathlib import Path
from integrate_ai.utils.typer_utils import TogglePromptOption
import os

batch_size_default = 16
instruction_polling_time_default = 30
log_interval_default = 10

app = typer.Typer(no_args_is_help=True)
logger = logging.getLogger(__name__)


@app.command()
def pull(
    token: str = TogglePromptOption(
        ...,
        help="The IAI token.",
        prompt="Please provide your IAI token",
        envvar="IAI_TOKEN",
    ),
    version: str = typer.Option("latest", "--version", "-v", help="The version of the docker image to pull."),
):
    """
    Pull the federated learning docker client.\n Defaults to the latest GPU version. Docker must be running for this command to work.
    """

    no_prompt = os.environ.get("IAI_DISABLE_PROMPTS")
    delete_response = False

    # start progress bar
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:

        # connect to docker
        p = progress.add_task(description="Connecting to docker...", total=1)
        docker_client = DockerClient(token)
        progress.update(task_id=p, completed=True)

        # check if any existing docker images on system
        p = progress.add_task(description="Searching for existing client images...", total=1)
        current_images = docker_client.get_local_versions(docker_client.docker_image_name)
        progress.update(task_id=p, completed=True)

        # check for latest docker image
        p = progress.add_task(description="Determining latest available client version...", total=1)
        docker_client.login()
        latest_available_version = docker_client.get_latest_available_version()
        progress.update(task_id=p, completed=True)

    version_to_pull = latest_available_version if version == "latest" else version
    if len(current_images) == 0:
        rprint("No existing client version found on system.")
    else:

        # if images exist on system, check the latest version that is installed
        latest_version = docker_client.get_latest_version_of_image(current_images) or "`latest`"
        rprint(
            f"Latest version of docker image found on system is {latest_version}. Most recent version is {latest_available_version}."
        )

        if latest_version == version_to_pull:

            # no point installing if they already have the latest image
            rprint("The requested version of the client image is already on your system. Exiting...")
            raise typer.Exit(0)
        else:
            prompt_msg = f"A newer version {latest_available_version} was found. The current version of the client image will be deleted from your system. Do you want to proceed?"
            # confirm that they are ok with deleting current client images on system
            prompt_msg = "Installing this client image will delete any current version of this image on your system. Do you want to proceed?"
            if no_prompt:
                delete_response = True
            else:
                delete_response = typer.confirm(prompt_msg)

    # delete current client images if they ok'd it
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        if delete_response:
            p = progress.add_task(
                description="Yes response received. Deleting existing client images...",
                total=1,
            )
            docker_client.delete_images(current_images)
            progress.update(task_id=p, completed=True)
        elif not delete_response and len(current_images) > 0:
            rprint("`No` response received. Exiting...")
            raise typer.Exit(0)

    # login and pull docker image
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        p = progress.add_task(description="Logging into docker repo...", total=1)
        login_result = docker_client.login()
        progress.update(task_id=p, completed=True)
        p = progress.add_task(
            description=f"Pulling docker image {version_to_pull}. This will take a few minutes...",
            total=1,
        )
        pull_result = docker_client.pull(repo=docker_client.docker_image_name, tag=version_to_pull)
        progress.update(task_id=p, completed=True)
        rprint(f"Image {version_to_pull} is now available.")
        raise typer.Exit(0)


@app.command()
def version():
    """
    The currently installed version of the docker client image.
    """
    docker_client = DockerClient()
    current_images = docker_client.get_local_versions(docker_client.docker_image_name)
    latest_version = docker_client.get_latest_version_of_image(current_images)
    if len(current_images) == 0:
        rprint("No client image found on system.")
    elif not latest_version:
        rprint("Found version tagged as `latest`.")
    else:
        rprint(latest_version)


@app.command()
def list(
    token: str = TogglePromptOption(
        ...,
        help="The IAI token.",
        prompt="Please provide your IAI token",
        envvar="IAI_TOKEN",
    )
):
    """
    List all available docker client images versions to pull.
    """
    docker_client = DockerClient(token)
    docker_client.login()
    versions = docker_client.get_versions()
    rprint("\n".join(versions))


# @app.command()
def log():
    """
    This command enables logging of the client docker container for debugging purposes.
    """
    pass  # pragma: no cover


# @app.command()
def train(
    token: str = TogglePromptOption(
        ...,
        help="Your generated IAI token.",
        prompt="Please provide your IAI token.",
        envvar="IAI_TOKEN",
    ),
    session: str = TogglePromptOption(
        ...,
        help="The session id to join for training.",
        prompt="Please provide the training session id.",
        envvar="IAI_SESSION",
    ),
    train_path: Path = TogglePromptOption(
        ...,
        help="Training dataset path.",
        prompt="Please provide the training dataset path",
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
    test_path: Path = TogglePromptOption(
        ...,
        help="Testing dataset path.",
        prompt="Please provide the testing dataset path",
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
    data_path: Path = TogglePromptOption(
        ...,
        help="Path for mounted directory.",
        prompt="Please provide the directory path to be mounted",
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
    client_name: str = typer.Option(
        None,
        "--client-name",
        help="The name used for client container",
    ),
    batch_size: int = typer.Option(batch_size_default, "--batch-size", help="Batch size to load the data with."),
    instruction_polling_time: int = typer.Option(
        instruction_polling_time_default,
        "--instruction-polling-time",
        help="Time to wait for new instructions in seconds.",
    ),
    log_interval: int = typer.Option(
        log_interval_default,
        "--log-interval",
        help="The logging frequency for training printout. ",
    ),
    approve_custom_package: bool = typer.Option(
        False,
        "--approve-custom-package",
        help="Flag to give pre-approval for training custom model package.",
    ),
    remove_after_complete: bool = typer.Option(
        False,
        "--remove-after-complete",
        help="Flag to remove container after training completed",
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Enables debug logging."),
):
    """
    Join a training session using the docker client.
    The client docker container will be deleted on completion.
    """
    docker_client = DockerClient()
    current_images = docker_client.get_local_versions(docker_client.docker_image_name)
    latest_version = docker_client.get_latest_version_of_image(current_images)

    mount_path = "/root/demo"

    if len(current_images) == 0:
        rich.print("No client image found on system.")
        rich.print("Exiting...")
        raise typer.Exit(0)

    image_name = f"{docker_client.docker_image_name}"
    if latest_version:
        image_name += ":" + latest_version

    existing_client_count = docker_client.count_existing_clients(image_name)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        container_name = client_name or f"client-{existing_client_count+1}"

        start_container_task = progress.add_task(description=f"Starting container {container_name}...", total=1)
        response = docker_client.run(
            image_name,
            detach=True,
            options={
                "tty": True,
                "name": container_name,
                "volumes": {
                    str(data_path): {"bind": mount_path, "mode": "ro"},
                },
            },
        )
        progress.update(task_id=start_container_task, completed=True)
        progress.console.print(f"Container {container_name} is started.", style="green")
        if verbose:
            logger.debug(response)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        start_training_task = progress.add_task(description=f"Start training...", total=1)
        container = docker_client.get_container(container_name)

        cmd = f"hfl train --token {token} --session-id {session}"
        cmd += f" --train-path {str(train_path).replace(str(data_path), mount_path)}"
        cmd += f" --test-path {str(test_path).replace(str(data_path), mount_path)}"
        cmd += f" --batch-size {batch_size}"
        cmd += f" --instruction-polling-time {instruction_polling_time}"
        cmd += f" --log-interval {log_interval}"
        if approve_custom_package:
            cmd += " --approve-custom-package"

        if verbose:
            logger.debug(f"Running command: {cmd}")

        exit_code, response = container.exec_run(
            cmd,
            stdout=verbose,
        )
        if exit_code:
            progress.console.print(f"Exit with exit_code {exit_code}, stopping...", style="red")
            progress.console.print(response, style=None)
            logger.error(response)
            container.stop()
            raise typer.Exit(0)
        else:
            progress.console.print(f"Finished training.", style="green")
            progress.console.print(response, style=None)
            logger.info(response)
            progress.update(task_id=start_training_task, completed=True)

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        closing_task = progress.add_task(description=f"Closing container...", total=1)
        container.stop()
        if remove_after_complete:
            container.remove()
        progress.update(task_id=closing_task, completed=True)

        raise typer.Exit(0)


@app.callback()
def main():
    """
    Sub command for managing client related operations.
    """
