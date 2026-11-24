from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, Text, false, func, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from db_models.base import Base


class MovieDBModel(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(
        ENUM("MSK", "SPB", name="Location", create_type=False), nullable=False
    )
    published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=false()
    )
    rating: Mapped[float] = mapped_column(
        Float, nullable=False, server_default=text("0")
    )
    genre_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
