from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MovieLocation(str, Enum):
    """Допустимые значения location в ответе Cinescope."""

    MSK = "MSK"
    SPB = "SPB"


class GenreResponse(BaseModel):
    """Жанр, вложенный в объект фильма в ответе GET /movies."""

    model_config = ConfigDict(extra="forbid")

    id: Optional[int] = None
    name: str


class MovieResponse(BaseModel):
    """Схема одного фильма из ответа GET /movies."""

    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    description: str
    genreId: int
    imageUrl: str
    price: int
    rating: float
    location: MovieLocation
    published: bool
    createdAt: datetime
    genre: GenreResponse


class MoviesPageResponse(BaseModel):
    """Схема страницы, которую возвращает GET /movies."""

    model_config = ConfigDict(extra="forbid")

    movies: list[MovieResponse]
    count: int
    page: int
    pageSize: int
    pageCount: int
