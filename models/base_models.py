from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict


class MovieLocation(str, Enum):
    MSK = "MSK"
    SPB = "SPB"


class GenreResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    name: str


class MovieGenreResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class MovieResponse(BaseModel):
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
    genre: MovieGenreResponse


class FindOneMovieResponse(MovieResponse):
    reviews: list[dict]


class MoviesPageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movies: list[MovieResponse]
    count: int
    page: int
    pageSize: int
    pageCount: int
