from ..api import RequestService
from ..endpoints import GenericPluralEndpoint


class ServiceItemsEndPoint(GenericPluralEndpoint):
    def __init__(self, request_service: RequestService, display_id=None):
        super(ServiceItemsEndPoint, self).__init__(request_service=request_service)
        self._endpoint = "/api/v2/service_catalog/items"
        self.resource_key = "service_items"
        self.display_id = display_id
        self.create_command = "place_request"

    @property
    def extended_url(self):
        url = super().extended_url
        if self.display_id is not None:
            url = f"{url}/{self.display_id}"
        return url
