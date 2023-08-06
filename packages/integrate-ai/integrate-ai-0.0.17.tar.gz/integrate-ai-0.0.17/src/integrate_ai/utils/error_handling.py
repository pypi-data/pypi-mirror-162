"""Module containing exception-related functionality."""

from requests import Response  # type: ignore
import typer
import os


class IntegrateAIException(Exception):
    """The general exception for request and response errors."""

    pass


class DockerException(Exception):
    """The general exception for docker-related errors."""

    pass


def check_for_IntegrateAIException(response):
    """Raises an IntegrateAIException from a response.

    If response has an error status code, raises a custom IntegrateAIException instead
      of the original Exception.

    Args:
        response (Response): HTTP response to check for error status and raise custom
          message for.

    Raises:
        IntegrateAIException: Customized IntegrateAI exception for the HTTP Exception.
    """

    try:
        response.raise_for_status()
    except Exception as e:
        data = response.json()
        if isinstance(data, dict) and "message" in data.keys():
            response_message = data.get("message")
        else:
            response_message = response.text
        raise IntegrateAIException(response_message) from e
