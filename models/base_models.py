from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from constants.roles import Roles

EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

class TestUser(BaseModel):
    """Тело запроса на создание пользователя (POST /register и POST /user)."""

    email: str = Field(..., pattern=EMAIL_PATTERN, description="Email пользователя")
    fullName: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=20)
    passwordRepeat: str = Field(..., min_length=8, max_length=20)
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    def check_password_repeat(cls, value: str, info) -> str:
        """passwordRepeat обязан совпадать с password."""
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("passwordRepeat не совпадает с password")
        return value


# Это Pydantic-модель данных, а не класс тестов для pytest.
TestUser.__test__ = False

class RegisterUserResponse(BaseModel):
    """Ответ на POST /register и POST /user."""

    id: str
    email: str = Field(..., pattern=EMAIL_PATTERN)
    fullName: str = Field(..., min_length=1, max_length=100)
    verified: bool
    banned: bool
    roles: list[Roles]
    createdAt: datetime


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
