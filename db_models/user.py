from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.orm import Mapped, mapped_column

from db_models.base import Base


class UserDBModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    banned: Mapped[bool] = mapped_column(Boolean, nullable=False)
    roles: Mapped[list[str] | None] = mapped_column(
        ARRAY(ENUM("USER", "ADMIN", "SUPER_ADMIN", name="Role", create_type=False)),
        nullable=True,
    )
