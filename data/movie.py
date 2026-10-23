from faker import Faker
from utils.data_generator import DataGenerator

fake = Faker(locale='ru_RU')
class MovieData:
    @staticmethod
    def create_movie_payload():
        return {
  "name": fake.sentence(nb_words=3),
  "imageUrl": "https://avatars.steamstatic.com/d3e0a9591723de214f8011ea61f0585d174728e0_full.jpg",
  "price": fake.random_int(min=100, max=333),
  "description": fake.text(max_nb_chars=133),
  "location": "SPB",
  "published": True,
  "genreId": 8
}