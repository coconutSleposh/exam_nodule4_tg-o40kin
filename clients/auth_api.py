from custom_requester.custom_requester import CustomRequester
from config.base_urls import AUTH_BASE_URL


class AuthApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=AUTH_BASE_URL)

    def login(self, username, password):
        return self.send_request(
            method="POST",
            endpoint="/login",
            data={"email": username, "password": password},
            expected_status=201
        )
