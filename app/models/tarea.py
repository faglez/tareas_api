from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Tarea(Base):
    __tablename__ = "tareas"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None]
    completada: Mapped[bool] = mapped_column(default=False)
    creado_en: Mapped[datetime] = mapped_column(server_default=func.now())
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))

    usuario: Mapped["Usuario"] = relationship(back_populates="tareas")
