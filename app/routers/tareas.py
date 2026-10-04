from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tarea, Usuario
from app.schemas import TareaCreate, TareaRead, TareaUpdate
from app.security import UsuarioActual

router = APIRouter(prefix="/tareas", tags=["tareas"])


def obtener_tarea(db: Session, tarea_id: int, usuario: Usuario) -> Tarea:
    tarea = db.get(Tarea, tarea_id)
    # 404 también si es de otro usuario, para no revelar que existe
    if tarea is None or tarea.usuario_id != usuario.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarea no encontrada")
    return tarea


@router.post("/", response_model=TareaRead, status_code=status.HTTP_201_CREATED)
def crear_tarea(datos: TareaCreate, usuario: UsuarioActual, db: Session = Depends(get_db)):
    tarea = Tarea(**datos.model_dump(), usuario_id=usuario.id)
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea


@router.get("/", response_model=list[TareaRead])
def listar_tareas(
    usuario: UsuarioActual,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    consulta = select(Tarea).where(Tarea.usuario_id == usuario.id).offset(skip).limit(limit)
    return db.scalars(consulta).all()


@router.get("/{tarea_id}", response_model=TareaRead)
def leer_tarea(tarea_id: int, usuario: UsuarioActual, db: Session = Depends(get_db)):
    return obtener_tarea(db, tarea_id, usuario)


@router.patch("/{tarea_id}", response_model=TareaRead)
def actualizar_tarea(
    tarea_id: int,
    datos: TareaUpdate,
    usuario: UsuarioActual,
    db: Session = Depends(get_db),
):
    tarea = obtener_tarea(db, tarea_id, usuario)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(tarea, campo, valor)
    db.commit()
    db.refresh(tarea)
    return tarea


@router.delete("/{tarea_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_tarea(tarea_id: int, usuario: UsuarioActual, db: Session = Depends(get_db)):
    tarea = obtener_tarea(db, tarea_id, usuario)
    db.delete(tarea)
    db.commit()
