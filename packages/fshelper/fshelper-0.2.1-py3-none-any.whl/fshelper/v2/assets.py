import logging
from typing import Dict, Optional

from ..api import RequestService
from ..endpoints import GenericPluralEndpoint


logger = logging.getLogger(__name__)


class AssetsEndPoint(GenericPluralEndpoint):
    """Endpoint for working with FreshService Assets"""

    def __init__(self, request_service: RequestService, identifier=None):
        super(AssetsEndPoint, self).__init__(request_service=request_service)
        self._endpoint = "/api/v2/assets"
        self.resource_key = "assets"
        self.identifier = identifier
        self._items_per_page = 100

    def delete(
        self, display_id: Optional[int] = None, permanently: Optional[bool] = False
    ) -> Dict:
        """Delete an asset with an option to additionally call the endpoint to permanently delete the item.

        Overriding the inherited method to include the option for a second API request to permanently delete the asset.
        :param display_id: Display ID for the asset to be deleted
        :param permanently: Flag to make a second call to the API to permanently delete the asset
        """
        _method = "DELETE"
        if display_id is not None:
            self.identifier = display_id
        _url = f"{self.item_extended_url}"
        logger.info("Deleting asset with display_id = '%d'", self.identifier)
        response = self.send_request(_url, method=_method)
        if permanently:
            _url = f"{self.item_extended_url}/delete_forever"
            _method = "PUT"
            logger.info(
                "Permanently deleting asset with display_id = '%d'", self.identifier
            )
            response = self.send_request(_url, method=_method)
        return response

    def restore(self, display_id: Optional[int] = None) -> Dict:
        if display_id is not None:
            self.identifier = display_id
        _method = "PUT"
        _url = f"{self.item_extended_url}/restore"
        response = self.send_request(_url, method=_method)
        return response

    def get_associated_requests(self, display_id: Optional[int] = None) -> Dict:
        if display_id is not None:
            self.identifier = display_id
        _url = f"{self.item_extended_url}/requests"
        response = self.send_request(_url)
        return response
