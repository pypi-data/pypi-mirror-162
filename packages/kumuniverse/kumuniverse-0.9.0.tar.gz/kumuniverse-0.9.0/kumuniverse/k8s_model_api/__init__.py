"""
Malacanang API Module for calling endpoints.
"""

import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import json


class ModelAPI:
    def __init__(self, env="dev"):
        """
        Initializes the Malacanang API.

        Parameters
        ----------
        env : str, optional
            Environment to be called (e.g. live or dev) (default is "dev")

        Attributes
        ----------
        headers : Object
            Headers to be passed into requests
        """
        self.headers = {"Content-Type": "application/json"}
        if env == "dev":
            # TODO: hostnames are only temporary
            self.base_url = "http://a964e32654136468fb87dfa602143604-d83587f2b0590882.elb.ap-southeast-1.amazonaws.com"
        elif env == "live":
            self.base_url = "http://a79af9dde217e490cbf62422d1abb943-90006a38fba4fba4.elb.ap-southeast-1.amazonaws.com"

    def invoke_endpoint_url(self, endpoint_url, request_body):
        """
        Invokes an endpoint URL given a request body.

        Parameters
        ----------
        endpoint_url : string, required
            Full URL string to be requested via POST method

        request_body : dict, required
            Model input as JSON dictionary

        Returns
        -------
        Any depending on the model's output
        """
        try:
            res = requests.post(
                url=endpoint_url, data=json.dumps(request_body), headers=self.headers
            )
            res.raise_for_status()
            return res.json()
        except HTTPError as errh:
            raise HTTPError("HTTP ERROR:", errh)
        except ConnectionError as errc:
            raise ConnectionError("CONNECTION ERROR:", errc)
        except Timeout as errt:
            raise Timeout("TIMEOUT ERROR:", errt)
        except RequestException as err:
            raise RequestException("REQUEST ERROR:", err)

    def invoke_endpoint_name(self, endpoint_name, request_body):
        """
        Uses endpoint_name to invoke a model deployed in dev/live environment with a request body.

        Parameters
        ----------
        endpoint_name : string, required
            Name of the model in dev/live

        request_body : dict, required
            Model input as JSON dictionary

        Returns
        -------
        Any depending on the model's output
        """
        try:
            endpoint_url = f"{self.base_url}/{endpoint_name}/predict"
            res = requests.post(
                url=endpoint_url, data=json.dumps(request_body), headers=self.headers
            )
            res.raise_for_status()
            return res.json()
        except HTTPError as errh:
            raise HTTPError("HTTP ERROR:", errh)
        except ConnectionError as errc:
            raise ConnectionError("CONNECTION ERROR:", errc)
        except Timeout as errt:
            raise Timeout("TIMEOUT ERROR:", errt)
        except RequestException as err:
            raise RequestException("REQUEST ERROR:", err)
