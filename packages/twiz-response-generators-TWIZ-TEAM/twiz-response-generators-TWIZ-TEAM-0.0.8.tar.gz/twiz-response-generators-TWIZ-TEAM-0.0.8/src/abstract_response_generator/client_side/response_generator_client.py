import json

from cobot_core import StateManager
from cobot_core.log.logger import LoggerFactory
from cobot_core.service_url_loader import ServiceURLLoader
import requests


class ResponseGeneratorClient:

    def __init__(self, url_module_name: str, timeout_in_millis: int = 1000):
        self.url = ServiceURLLoader.get_url_for_module(url_module_name)
        self.timeout_in_millis = timeout_in_millis
        self.logger = LoggerFactory.setup(self)

    def run(self, request_data):
        response = requests.post(self.url,
                                 data=request_data,
                                 headers={'content-type': 'application/json'},
                                 timeout=self.timeout_in_millis / 1000.0)
        result = response.json()

        twiz_response = result.get("response", None)
        if twiz_response:
            return twiz_response
        raise Exception("Unable to get response")