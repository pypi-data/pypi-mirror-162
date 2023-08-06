from cobot_core.service_module import LocalServiceModule


class LocalResponseGenerator(LocalServiceModule):
    def execute(self):
        """
        TODO: This method is meant to be overwritten.
        It should have the following:
        1) Create a response generator client with the necessary corresponding parameters
        2) Call the run() function and return the clients response
        NOTE: The url_module_name parameter requires the remote response generator to be registered in the twiz_bot.py
        """
