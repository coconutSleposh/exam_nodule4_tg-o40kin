from models.base_models import RegisterUserResponse


class TestAuth:

    def test_register_user(self, api_manager, test_user):
        response = api_manager.auth_api.register(test_user)
        registered_user = RegisterUserResponse(**response.json())

        assert registered_user.email == test_user.email
        assert registered_user.fullName == test_user.fullName
        assert registered_user.roles == test_user.roles
        assert registered_user.verified is True
        assert registered_user.banned is False
