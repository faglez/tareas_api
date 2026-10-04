from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tarea, Usuario
from app.schemas import TareaRead, UsuarioRead, UsuarioUpdate
from app.security import UsuarioActual, hashear_password

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def verificar_propietario(usuario_id: int, usuario: Usuario) -> None:
    if usuario_id != usuario.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No tienes permiso sobre este usuario")


def verificar_email_libre(db: Session, email: str) -> None:
    if db.scalar(select(Usuario).where(func.lower(Usuario.email) == email.lower())):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El email ya está registrado")


@router.get("/me", response_model=UsuarioRead)
def leer_usuario_actual(usuario: UsuarioActual):
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioRead)
def leer_usuario(usuario_id: int, usuario: UsuarioActual):
    verificar_propietario(usuario_id, usuario)
    return usuario


@router.get("/{usuario_id}/tareas", response_model=list[TareaRead])
def listar_tareas_de_usuario(
    usuario_id: int, usuario: UsuarioActual, db: Session = Depends(get_db)
):
    verificar_propietario(usuario_id, usuario)
    return db.scalars(select(Tarea).where(Tarea.usuario_id == usuario.id)).all()


@router.patch("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(
    usuario_id: int,
    datos: UsuarioUpdate,
    usuario: UsuarioActual,
    db: Session = Depends(get_db),
):
    verificar_propietario(usuario_id, usuario)
    cambios = datos.model_dump(exclude_unset=True)
    if "email" in cambios and cambios["email"].lower() != usuario.email.lower():
        verificar_email_libre(db, cambios["email"])
    if "password" in cambios:
        cambios["hashed_password"] = hashear_password(cambios.pop("password"))
    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_usuario(usuario_id: int, usuario: UsuarioActual, db: Session = Depends(get_db)):
    verificar_propietario(usuario_id, usuario)
    db.delete(usuario)
    db.commit()
