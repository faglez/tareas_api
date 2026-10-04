from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Usuario

password_hash = PasswordHash.recommended()  # Argon2

# Lee la cabecera "Authorization: Bearer <token>"; tokenUrl es para el botón Authorize de /docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hashear_password(password: str) -> str:
    return password_hash.hash(password)


def verificar_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def crear_token(usuario_id: int) -> str:
    expira = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(usuario_id), "exp": expira}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Usuario:
    credenciales_invalidas = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        usuario_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise credenciales_invalidas
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise credenciales_invalidas
    return usuario


UsuarioActual = Annotated[Usuario, Depends(get_current_user)]
