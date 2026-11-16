from resources.user_creds import SuperAdminCreds
import logging
import pytest
from pydantic import ValidationError
from models.base_models import RegisterUserResponse, TestUser as TestUserModel


logger = logging.getLogger(__name__)


class TestUser:

    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data)
        created_user = RegisterUserResponse(**response.json())

        assert created_user.email == creation_user_data.email
        assert created_user.fullName == creation_user_data.fullName
        assert created_user.roles == creation_user_data.roles
        assert created_user.verified is True

    def test_get_user_by_locator(self, super_admin, creation_user_data):
        created_user_response = super_admin.api.user_api.create_user(creation_user_data)
        created_user = RegisterUserResponse(**created_user_response.json())
        response_by_id = RegisterUserResponse(**super_admin.api.user_api.get_user(created_user.id).json())
        response_by_email = RegisterUserResponse(**super_admin.api.user_api.get_user(creation_user_data.email).json())

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.id
        assert response_by_id.email == creation_user_data.email
        assert response_by_id.fullName == creation_user_data.fullName
        assert response_by_id.roles == creation_user_data.roles
        assert response_by_id.verified is True

    def test_get_user_by_common_user(self, common_user):
        common_user.api.user_api.get_user(
            SuperAdminCreds.USERNAME,
            expected_status=403
        )

    def test_test_user_model(self, test_user):
        testuser = test_user
        logger.info("model_dump_json(): %s", testuser.model_dump_json())
        logger.info("model_dump_json(exclude_unset=True): %s",
                    testuser.model_dump_json(exclude_unset=True))
        logger.info("model_dump_json(exclude_none=True): %s",
                    testuser.model_dump_json(exclude_none=True))
        logger.info("model_dump(): %s", testuser.model_dump())

        data_without_roles = test_user.model_dump(exclude_unset=True)
        data_without_roles.pop("roles")
        testuser_without_roles = TestUserModel(**data_without_roles)

        logger.info("model_dump_json() без roles: %s",
                    testuser_without_roles.model_dump_json())
        logger.info("model_dump_json(exclude_unset=True) без roles: %s",
                    testuser_without_roles.model_dump_json(exclude_unset=True))
        logger.info("model_dump_json(exclude_none=True) без roles: %s",
                    testuser_without_roles.model_dump_json(exclude_none=True))

    def test_password_repeat_matches_password(self, test_user):
        assert test_user.passwordRepeat == test_user.password

    def test_password_repeat_mismatch(self, test_user):
        invalid_data = test_user.model_dump(exclude_unset=True)
        invalid_data["password"] = "Password123"
        invalid_data["passwordRepeat"] = "Different123"

        with pytest.raises(ValidationError) as exc_info:
            TestUserModel(**invalid_data)

        logger.info("Ожидаемая ошибка несовпадения паролей:\n%s", exc_info.value)

    def test_invalid_email_rejected(self, test_user):
        invalid_data = test_user.model_dump(exclude_unset=True)
        invalid_data["email"] = "не-почта"

        with pytest.raises(ValidationError) as exc_info:
            TestUserModel(**invalid_data)

        logger.info("Ожидаемая ошибка формата email:\n%s", exc_info.value)

    def test_user_model_rejects_invalid_email(self):
        with pytest.raises(ValidationError):
            TestUserModel(
                email="не-почта",
                fullName="Иван",
                password="12345678",
                passwordRepeat="12345678",
            )
