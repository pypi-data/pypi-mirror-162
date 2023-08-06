import json

from typing import Optional

import requests

from abstract_rg_apl_builder import ResponseGeneratorAPLBuilder
from abstract_rg_update_state import ResponseGeneratorUpdateState


class ResponseGeneratorController:
    state_updater: ResponseGeneratorUpdateState
    apl_builder: ResponseGeneratorAPLBuilder
    response_string_url: str
    timeout_in_millis: int

    def __init__(self, state_updater: ResponseGeneratorUpdateState,
                 apl_builder: ResponseGeneratorAPLBuilder, response_string_url: str, user_id: str,
                 timeout_in_millis: int = 1000):
        self.state_updater = state_updater
        self.apl_builder = apl_builder
        self.response_string_url = response_string_url
        self.timeout_in_millis = timeout_in_millis
        self.user_id = user_id

    def run(self, generate_response: bool = True) -> Optional[dict]:
        """
        Invoke ResponseGeneratorUpdateState, ResponseStringController
        and other MLRemoteModule if required.
        """
        # 1. Update necessary state attributes
        twiz_state = self.state_updater.run()

        if generate_response:
            # 2. Get response string from response string controller microservice
            try:
                data = {'user_id': self.user_id}
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

                response_string = requests.post(self.response_string_url,
                                                headers=headers,
                                                data=json.dumps(data),
                                                timeout=self.timeout_in_millis / 1000.0)
                response_string_json = response_string.json()
                response = response_string_json.get("responsestring", None)
            except Exception as e:
                print("ERROR: Unable to get responsestring")
                return None
            if not response:
                print("ERROR: Unable to get responsestring")
                return None

            # 3. Get apl doc and directives if needed
            if twiz_state.curr().is_apl_supported:
                directives = self.apl_builder.run(twiz_state)

            # 4. Return adequate response depending whether device supports apl
                if directives:
                    return {'response': response, 'directives': directives}

            return {'response': response}

        return {'response': ''}  # should only happen when we wish to ignore the response
