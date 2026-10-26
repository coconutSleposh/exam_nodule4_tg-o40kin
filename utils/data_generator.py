from faker import Faker


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
