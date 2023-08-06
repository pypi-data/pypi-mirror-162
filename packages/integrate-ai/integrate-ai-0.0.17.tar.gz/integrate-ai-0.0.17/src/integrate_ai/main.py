"""Module containing top-level Typer app functionality."""

import typer
import integrate_ai.sdk as sdk
import integrate_ai.client as client

app = typer.Typer(no_args_is_help=True)

app.add_typer(sdk.app, name="sdk")
app.add_typer(client.app, name="client")


@app.callback()
def docs(
    no_prompt: bool = typer.Option(False, "--no-prompt", help="Disable prompts. Confirmations will default to `Y`.")
):
    """
    The CLI interface to manage integrate.ai operations.

    Your IAI token will be required in many commmands. For convenience, you can set this in the `IAI_TOKEN` environment variable to avoid repeated prompts.
    """
    pass


def main():

    app()


if __name__ == "__main__":
    main()  # pragma: no cover
