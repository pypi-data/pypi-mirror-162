class ServiceRequestModel:
    """
    https://api.freshservice.com/v2/#create_service_request
    {
        "quantity": 1,
        "email": "sample@freshservice.com",
        "custom_fields":{
            "hello" : "test",
            "link" : "https://freshservice.com/"
        },
        "child_items" : [{
            "service_item_id": 22,
            "quantity": 1,
            "custom_fields" : {
                "child_1": "test"
            }
        }]
    }
    """

    def __init__(
        self,
        requester_email: str,
        custom_field_data: dict,
        requested_for=None,
        quantity=1,
    ):
        self.quantity = quantity
        self.email = requester_email
        self.custom_fields = custom_field_data
        self.requested_for = requested_for
