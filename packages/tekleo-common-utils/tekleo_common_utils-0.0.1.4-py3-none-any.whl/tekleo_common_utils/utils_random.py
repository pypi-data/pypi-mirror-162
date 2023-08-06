from injectable import injectable
import random
from string import ascii_lowercase, ascii_uppercase
from user_agent import generate_user_agent
from faker import Faker
import namesgenerator


@injectable
class UtilsRandom:
    def __init__(self):
        self.CHARS_ASCII = []
        self.CHARS_ASCII.extend(ascii_lowercase)
        self.CHARS_ASCII.extend(ascii_uppercase)
        self.faker = Faker()

    def get_random_string(self, size: int) -> str:
        return ''.join([random.choice(self.CHARS_ASCII) for i in range(0, size)])

    def get_random_user_agent(self) -> str:
        return str(generate_user_agent())

    def get_random_ip(self) -> str:
        return '.'.join([str(random.randint(0, 255)) for i in range(0, 4)])

    def get_random_year(self, min_year: int = 1910, max_year: int = 2022) -> int:
        return random.randint(min_year, max_year)

    def get_random_docker_name(self) -> str:
        return namesgenerator.get_random_name()

    def get_random_full_name(self) -> str:
        return self.faker.name()

    def get_random_first_name(self) -> str:
        return self.faker.first_name()

    def get_random_last_name(self) -> str:
        return self.faker.last_name()

    def get_random_country(self) -> str:
        return self.faker.country()