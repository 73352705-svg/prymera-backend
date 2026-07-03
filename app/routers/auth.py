from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, decode_token
from app.models import Asesor
from app.schemas import LoginRequest, LoginResponse, AsesorOut

router = APIRouter(prefix="/auth", tags=["Auth"])

BLOQUEO_MINUTOS = 30
MAX_INTENTOS = 5


def get_asesor_actual(token: str = Header(alias="Authorization"), db: Session = Depends(get_db)) -> Asesor:
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    payload = decode_token(token.replace("Bearer ", ""))
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido")
    asesor = db.query(Asesor).filter(Asesor.id == payload["sub"]).first()
    if not asesor:
        raise HTTPException(status_code=404, detail="Asesor no encontrado")
    return asesor


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    asesor = db.query(Asesor).filter(Asesor.codigo_empleado == req.codigo_empleado).first()
    if not asesor:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    if not asesor.activo:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    ahora = datetime.now(timezone.utc)
    if asesor.bloqueado_hasta and asesor.bloqueado_hasta > ahora:
        restante = int((asesor.bloqueado_hasta - ahora).total_seconds() // 60)
        raise HTTPException(status_code=429, detail=f"Cuenta bloqueada. Intenta en {restante} min")

    if not verify_password(req.password, asesor.password_hash):
        asesor.intentos_fallidos = (asesor.intentos_fallidos or 0) + 1
        if asesor.intentos_fallidos >= MAX_INTENTOS:
            asesor.bloqueado_hasta = ahora + timedelta(minutes=BLOQUEO_MINUTOS)
        db.commit()
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    asesor.intentos_fallidos = 0
    asesor.bloqueado_hasta = None
    db.commit()

    token = create_access_token({"sub": str(asesor.id), "perfil": asesor.perfil})
    return LoginResponse(
        access_token=token,
        asesor=AsesorOut(
            id=str(asesor.id),
            codigo_empleado=asesor.codigo_empleado,
            nombres=asesor.nombres,
            apellidos=asesor.apellidos,
            agencia_id=str(asesor.agencia_id) if asesor.agencia_id else None,
            perfil=asesor.perfil,
        ),
    )


@router.get("/me", response_model=AsesorOut)
def me(asesor: Asesor = Depends(get_asesor_actual)):
    return AsesorOut(
        id=str(asesor.id),
        codigo_empleado=asesor.codigo_empleado,
        nombres=asesor.nombres,
        apellidos=asesor.apellidos,
        agencia_id=str(asesor.agencia_id) if asesor.agencia_id else None,
        perfil=asesor.perfil,
    )
