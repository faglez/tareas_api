from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TareaBase(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descripcion: str | None = None


class TareaCreate(TareaBase):
    pass


class TareaUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    descripcion: str | None = None
    completada: bool | None = None


class TareaRead(TareaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    completada: bool
    usuario_id: int
    creado_en: datetime
