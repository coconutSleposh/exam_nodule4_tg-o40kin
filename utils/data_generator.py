from faker import Faker
from datetime import datetime
from uuid import uuid4


class DataGenerator:
    fake = Faker(locale='ru_RU')

    @staticmethod
    def generate_random_email():
        return DataGenerator.fake.email()

    @staticmethod
    def generate_random_name():
        return DataGenerator.fake.name()

    @staticmethod
    def generate_random_password():
        return DataGenerator.fake.password(
            length=12,
            special_chars=False,
            digits=True,
            upper_case=True,
            lower_case=True
        )

    @staticmethod
    def generate_user_data() -> dict:
        """Generate fields that are stored directly in the users table."""
        now = datetime.now()
        return {
            "id": str(uuid4()),
            "email": DataGenerator.generate_random_email(),
            "full_name": DataGenerator.generate_random_name(),
            "password": DataGenerator.generate_random_password(),
            "created_at": now,
            "updated_at": now,
            "verified": False,
            "banned": False,
            "roles": ["USER"],
        }
