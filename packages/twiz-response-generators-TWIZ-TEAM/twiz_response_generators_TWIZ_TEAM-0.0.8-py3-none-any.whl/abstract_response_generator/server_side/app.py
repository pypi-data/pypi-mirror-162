#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import sys
from typing import Optional

from flask import Flask, request, Response
from flask_restful import reqparse, Api, Resource

from pip_libraries_code.response_generator.src.abstract_response_generator.server_side.abstract_rg_apl_builder import \
    ResponseGeneratorAPLBuilder
from pip_libraries_code.response_generator.src.abstract_response_generator.server_side.abstract_rg_controller import \
    ResponseGeneratorController
from pip_libraries_code.response_generator.src.abstract_response_generator.server_side.abstract_rg_update_state import \
    ResponseGeneratorUpdateState

app = Flask("remote module")
api = Api(app)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

required_context = ['generate_response', 'response_string_url', 'user_id']


class RemoteResponseGenerator(Resource):
    response_generator_controller: Optional[ResponseGeneratorController] = None
    args: Optional[dict] = None

    def get(self):
        return 200

    def post(self):
        t0 = time.time()

        args = request.get_json(force=True)

        app.logger.info("Input received: " + str(args))
        validation = self.__validate_input(args)  # updates self.args value
        if validation:
            return validation, 500

        ret = {}

        ret.update(
            self.run_response_generator(self.args.get('user_id'))
        )

        ret['performance'] = time.time() - t0,
        ret['error'] = False

        return ret, 200

    def __validate_input(self, args) -> Optional[dict]:
        message = ""
        # changed this method w.r.t the original because it considered zero and None as empty which is not correct
        for ctx in required_context:
            if ctx in args:
                ctx_value = args.get(ctx)
                if ctx_value is None:
                    app.logger.info(f"Key: {ctx} has value None. Check if this is the correct behaviour.")
            else:
                app.logger.info("Context missing: " + str(ctx))
                message += "Context missing: " + ctx
        if message:
            return {
                'message': message,
                'error': True
            }
        self.args = args
        return None

    def _get_response(self) -> Optional[dict]:
        if self.response_generator_controller is None or self.args is None:
            app.logger.info("Error: response generator controller still not initialized")
            return {
                'response': 'Error: response generator controller still not initialized'
            }
        response = self.response_generator_controller.run(self.args.get('generate_response', True))

        if response is None:
            app.logger.info("Error: response generator unable to get response string")
            return {
                'response': 'Error: response generator unable to get response string'
            }

        app.logger.info("result: %s", response)
        return response

    def _set_response_generator_controller(self, rg_state: ResponseGeneratorUpdateState,
                                           rg_apl: ResponseGeneratorAPLBuilder) -> None:
        if self.response_generator_controller is None \
                and self.args is not None \
                and rg_state is not None \
                and rg_apl is not None:
            self.response_generator_controller = ResponseGeneratorController(rg_state,
                                                                             rg_apl,
                                                                             self.args.get('response_string_url'),
                                                                             self.args.get('user_id'))

    """
    ###### IMPORTANT: THIS IS THE ONLY METHOD THAT SHOULD BE OVERWRITTEN ######
    """

    def run_response_generator(self, user_id: str) -> Optional[dict]:
        """
        TODO: This method is meant to be overwritten.
        It should have the following:
        1) Call self._set_response_generator_controller(...)
        2) return self._get_response()
        """


api.add_resource(RemoteResponseGenerator, '/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=os.environ.get('REMOTE_MODULE_PORT') or 5001)
