from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Text, false, func
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.orm import Mapped, mapped_column

from db_models.base import Base


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


_role_type = ENUM(
    UserRole,
    name="Role",
    values_callable=lambda roles: [role.value for role in roles],
    create_type=False,
)


class UserDBModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=false()
    )
    banned: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=false()
    )
    roles: Mapped[list[UserRole] | None] = mapped_column(
        ARRAY(_role_type), nullable=True
    )
