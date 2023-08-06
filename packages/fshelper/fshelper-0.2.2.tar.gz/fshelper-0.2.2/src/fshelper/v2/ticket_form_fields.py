from ..api import RequestService
from ..endpoints import GenericPluralEndpoint


class TicketFormFieldsEndPoint(GenericPluralEndpoint):
    def __init__(self, request_service: RequestService):
        super(TicketFormFieldsEndPoint, self).__init__(request_service=request_service)
        self._endpoint = "/api/v2/ticket_form_fields"
        self.resource_key = "ticket_fields"
