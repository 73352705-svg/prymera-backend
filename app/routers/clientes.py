from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Cliente, Credito, CreditoPreaprobado
from app.schemas import ClienteOut, FichaClienteOut

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/{cliente_id}/ficha", response_model=FichaClienteOut)
def ficha_cliente(cliente_id: str, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    creditos = db.query(Credito).filter(Credito.cliente_id == cliente_id).all()
    deuda_total = sum(c.saldo_total or 0 for c in creditos)
    cuotas_mora = sum(1 for c in creditos if (c.dias_mora or 0) > 0)
    cuotas_al_dia = sum((c.cuotas_pagadas or 0) for c in creditos)

    return FichaClienteOut(
        cliente=ClienteOut(
            id=str(cliente.id),
            numero_documento=cliente.numero_documento,
            nombres=cliente.nombres,
            apellidos=cliente.apellidos,
            telefono=cliente.telefono,
            direccion=cliente.direccion,
            tipo_negocio=cliente.tipo_negocio,
            nombre_negocio=cliente.nombre_negocio,
            lat=cliente.lat,
            lng=cliente.lng,
        ),
        deuda_total=deuda_total,
        cuotas_al_dia=cuotas_al_dia,
        cuotas_mora=cuotas_mora,
        fecha_ultimo_pago=None,
        calificacion_sbs=cliente.calificacion_sbs,
    )


@router.post("/{cliente_id}/ubicacion")
def actualizar_ubicacion(cliente_id: str, lat: float, lng: float, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente.lat = lat
    cliente.lng = lng
    db.commit()
    return {"ok": True}
