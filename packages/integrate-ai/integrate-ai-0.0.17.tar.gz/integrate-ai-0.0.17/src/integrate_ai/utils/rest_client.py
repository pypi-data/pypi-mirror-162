"""
Module containing REST interface functionality.

This contains a `RestClient` class that will be used to interface with the IAI REST API.
"""

import jwt
from typing import Any, Dict
from integrate_ai.utils.error_handling import check_for_IntegrateAIException
from typing import Optional
import requests
import os


class RestClient:
    """Client class for interacting with the integrate.ai API.

    This class includes functionality for performing various operations using
      the integrate.ai REST API.
    This class requires a valid token before it can perform its operations.
    """

    def __init__(self, token: str):
        """Initiates a client given a valid decoded IAI token object.

        Args:
            token (str): IAI token."""

        self.auth_token: str = token
        decoded_token: Dict[str, str] = self._decode_jwt_token(token=token)
        self.customer: str = decoded_token["customer"]
        self.env: str = decoded_token["env"]
        self.api_url: str = self._get_api_endpoint()
        self.gateway_url: str = self._get_gateway_endpoint()

    def _headers(self) -> Dict[str, str]:
        """Add authenticating headers for use with REST API."""

        header = {"content-type": "application/json"}
        header["Authorization"] = f"Bearer {self.auth_token}"
        return header

    def _decode_jwt_token(self, token: str, secret: str = "", verify_signature: bool = False) -> Dict[str, str]:
        """Decodes a JWT token."""
        decoded_token = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_signature": verify_signature},
        )
        return decoded_token

    def _get_api_endpoint(self) -> str:
        """Returns API endpoint."""
        api_endpoint = os.environ.get("IAI_DEBUG_API_URL")
        if not api_endpoint:
            endpoint = f"https://iai-api-{self.customer}-{self.env}.integrateai.net"

        return endpoint

    def _get_gateway_endpoint(self) -> str:
        """Returns Gateway endpoint."""

        gateway_endpoint = os.environ.get("IAI_DEBUG_GATEWAY_URL")
        if not gateway_endpoint:
            endpoint = f"https://iai-fl-gateway-{self.customer}-{self.env}.integrateai.net"

        return endpoint

    def make_get_request(self, url: str, body={}, headers=None) -> Dict[str, str]:
        """Performs a GET request using client.

        Args:
            url (str): URL to make GET request to.
            body (Dict): body to include in GET request.
            headers (Dict): The headers to be added to the GET request.
                Defaults to the integrate.ai API Authorization headers.

        Returns:
            response (Dict[str,str]): JSON response from GET request.

        Raises:
            IntegrateAIException: If error in GET request."""
        request_headers = self._headers()
        if headers:
            request_headers.update(headers)
        response = requests.get(url, headers=request_headers, json=body)
        check_for_IntegrateAIException(response)
        return response.json()

    def get_ecr_token(self) -> Dict[str, str]:
        """Retrieves an ECR token using IAI token.

        Returns:
            ecr_response (Dict[str,str]): response to ECR GET request."""
        url = f"{self.api_url}/fl/ecr/token"
        ecr_response = self.make_get_request(url)

        return ecr_response

    def get_pip_install_command(self, version="", package="") -> Dict[str, str]:
        """Get pip install command to install sdk.
        Args:
            version (str): Version of sdk to install.
            package (str): Package name to install.
        Returns:
                A Dict of the form
                ```
                {
                    "pipInstallCommand":"<pip_install_command>",
                }
                ```
        Raises:
            IntegrateAIException: Customized IntegrateAI exception for the HTTP Exception.
        """
        url = f"{self.api_url}/fl/pip/{package}"
        if version:
            url += f"/{version}"
        response = requests.get(
            url,
            headers=self._headers(),
        )
        check_for_IntegrateAIException(response=response)

        return response.json()

    def get_package_versions(self, package="") -> Dict[str, Any]:
        """Get package versions.
        Args:
            package (str): Name of package that has a list of available versions.
        Returns:
                A Dict of the form
                ```
            {
                "package_name": "<package-name>",
                "package_versions": [
                    {
                        "version": <version_number_1>,
                        "revision": <revision_string>,
                        "status": "Published"
                    },
                    {
                        "version": <version_number_2>,
                        "revision": <revision_string>,
                        "status": "Published"
                    }
                ]
            }
                ```
        Raises:
            IntegrateAIException: Customized IntegrateAI exception for the HTTP Exception.
        """
        url = f"{self.api_url}/fl/pip/{package}/list"
        response = requests.get(
            url,
            headers=self._headers(),
        )
        check_for_IntegrateAIException(response=response)

        return response.json()
