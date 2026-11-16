"""Модели песочницы. Повторяют реальную структуру ответов Cinescope /movies."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StrictBase(BaseModel):
    """Общая настройка: неизвестные поля запрещены во всех вложенных моделях."""
    model_config = ConfigDict(extra="forbid")

class Location(str, Enum):
    MSK = "MSK"
    SPB = "SPB"

# --- самые внутренние модели ---

class Genre(StrictBase):
    """Жанр внутри фильма. Приходит как {"name": "Драма"}."""
    id: Optional[int] = None
    name: str

class ReviewUser(StrictBase):
    """Автор отзыва. Приходит как {"fullName": "Melissa Ellis"}."""
    fullName: str

# --- средний уровень ---

class Review(StrictBase):
    userId: str
    text: str
    rating: int = Field(..., ge=0, le=5)
    createdAt: datetime
    user: ReviewUser            # вложенная модель

class Movie(StrictBase):
    id: int = Field(strict=True)
    name: str
    description: str
    genreId: int
    imageUrl: str
    price: int
    rating: float = Field(..., ge=0, le=5)
    location: Location
    published: bool
    createdAt: datetime
    genre: Genre                # вложенная модель

# --- то, что реально возвращают эндпоинты ---

class MoviesPage(StrictBase):
    """Ответ GET /movies - страница со списком фильмов."""
    movies: list[Movie]         # список вложенных моделей
    count: int
    page: int
    pageSize: int
    pageCount: int

class MovieDetails(Movie):
    """Ответ GET /movies/{id} - тот же фильм, но ещё и с отзывами.

    Наследуемся от Movie, чтобы не переписывать 11 полей заново.
    """
    reviews: list[Review]
