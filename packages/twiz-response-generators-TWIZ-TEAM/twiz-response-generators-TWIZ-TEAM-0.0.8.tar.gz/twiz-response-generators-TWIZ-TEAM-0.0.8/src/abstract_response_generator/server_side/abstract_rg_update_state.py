from state_access.twiz_state import TwizState


class ResponseGeneratorUpdateState:
    _twiz_state: TwizState

    def __init__(self, user_id: str):
        self._twiz_state = TwizState(user_id)

    def run(self) -> TwizState:
        """
        Have a switch depending on possible state values invoking an aux method per if statement. Returns the final
        TwizState so Contoller can interpret and forward to ResponseGeneratorAPLBuilder and ResponseStringController.
        """

    """
    Each aux_method (one per if statement of run) must have two clear phases: 
        1) updating current_state; 
        2) updating user_state;
    """
