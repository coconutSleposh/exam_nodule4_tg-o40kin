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

    def register(self, user_data, expected_status=201):
        return self.send_request(
            method="POST",
            endpoint="/register",
            data=user_data,
            expected_status=expected_status
        )

    def authenticate(self, user_creds):
        email = user_creds[0]
        password = user_creds[1]
        response_data = self.login(username=email, password=password).json()
        if 'accessToken' not in response_data:
            raise KeyError('Отсутствует токен')
        token = response_data['accessToken']
        self._update_session_headers({"Authorization": "Bearer " + token})
