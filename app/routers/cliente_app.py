from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, decode_token
from app.models import UsuarioCliente, Cliente, Credito, Tarjeta, OperacionCliente
from app.schemas import ClienteLoginRequest, ClienteLoginResponse, ClienteOut, OperacionCreate, OperacionOut

router = APIRouter(prefix="/cliente-app", tags=["Cliente App"])


@router.post("/login", response_model=ClienteLoginResponse)
def login_cliente(req: ClienteLoginRequest, db: Session = Depends(get_db)):
    user = db.query(UsuarioCliente).filter(UsuarioCliente.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    cliente = db.query(Cliente).filter(Cliente.id == user.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    token = create_access_token({"sub": str(cliente.id), "tipo": "cliente"})
    return ClienteLoginResponse(
        token=token,
        cliente=ClienteOut(
            id=str(cliente.id),
            numero_documento=cliente.numero_documento,
            nombres=cliente.nombres,
            apellidos=cliente.apellidos,
            telefono=cliente.telefono,
            direccion=cliente.direccion,
        ),
    )


@router.get("/creditos")
def mis_creditos(cliente_id: str, db: Session = Depends(get_db)):
    creditos = db.query(Credito).filter(Credito.cliente_id == cliente_id).all()
    return [
        {
            "id": str(c.id),
            "cod_cuenta": c.cod_cuenta_credito,
            "producto": c.producto,
            "monto_desembolsado": c.monto_desembolsado,
            "saldo_total": c.saldo_total,
            "dias_mora": c.dias_mora,
            "estado": c.estado,
            "cuotas_pagadas": c.cuotas_pagadas,
            "cuotas_total": c.cuotas_total,
            "tea": c.tea,
        }
        for c in creditos
    ]


@router.get("/tarjetas")
def mis_tarjetas(cliente_id: str, db: Session = Depends(get_db)):
    tarjetas = db.query(Tarjeta).filter(Tarjeta.cliente_id == cliente_id).all()
    return [
        {
            "id": str(t.id),
            "numero_enmascarado": t.numero_enmascarado,
            "marca": t.marca,
            "linea_credito": t.linea_credito,
            "saldo_utilizado": t.saldo_utilizado,
            "estado": t.estado,
        }
        for t in tarjetas
    ]


@router.post("/operaciones", response_model=OperacionOut)
def crear_operacion(data: OperacionCreate, cliente_id: str, db: Session = Depends(get_db)):
    op = OperacionCliente(
        cliente_id=cliente_id,
        cod_cuenta_origen=data.cod_cuenta_origen,
        cod_cuenta_destino=data.cod_cuenta_destino,
        tipo=data.tipo,
        monto=data.monto,
        moneda=data.moneda,
    )
    db.add(op)
    db.commit()
    db.refresh(op)
    return OperacionOut(
        id=str(op.id),
        tipo=op.tipo,
        monto=op.monto,
        estado=op.estado,
        created_at=op.created_at,
    )


@router.get("/operaciones", response_model=list[OperacionOut])
def historial_operaciones(cliente_id: str, db: Session = Depends(get_db)):
    ops = (
        db.query(OperacionCliente)
        .filter(OperacionCliente.cliente_id == cliente_id)
        .order_by(OperacionCliente.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        OperacionOut(
            id=str(op.id),
            tipo=op.tipo,
            monto=op.monto,
            estado=op.estado,
            created_at=op.created_at,
        )
        for op in ops
    ]
