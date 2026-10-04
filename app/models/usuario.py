from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.tarea import Tarea


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    creado_en: Mapped[datetime] = mapped_column(server_default=func.now())

    tareas: Mapped[list["Tarea"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
