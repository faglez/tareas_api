from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.routers.usuarios import verificar_email_libre
from app.schemas import Token, UsuarioCreate, UsuarioRead
from app.security import crear_token, hashear_password, verificar_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/registro", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def registro(datos: UsuarioCreate, db: Session = Depends(get_db)):
    verificar_email_libre(db, datos.email)
    usuario = Usuario(
        **datos.model_dump(exclude={"password"}),
        hashed_password=hashear_password(datos.password),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # En OAuth2 el campo se llama "username"; aquí contiene el email
    usuario = db.scalar(
        select(Usuario).where(func.lower(Usuario.email) == form.username.lower())
    )
    if usuario is None or not verificar_password(form.password, usuario.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=crear_token(usuario.id))
