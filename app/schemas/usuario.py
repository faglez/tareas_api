from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    password: str = Field(min_length=8, max_length=128)


class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    creado_en: datetime
