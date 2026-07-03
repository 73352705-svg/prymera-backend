from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import AccionCobranza, Credito, CarteraDiaria, Cliente
from app.schemas import AccionCobranzaCreate, MoraItemOut

router = APIRouter(prefix="/cobranza", tags=["Cobranza"])


@router.get("/mora", response_model=list[MoraItemOut])
def listar_mora(asesor_id: str, db: Session = Depends(get_db)):
    cartera = (
        db.query(CarteraDiaria)
        .filter(
            CarteraDiaria.asesor_id == asesor_id,
            CarteraDiaria.tipo_gestion == "RECUPERACION_MORA",
        )
        .all()
    )
    result = []
    for item in cartera:
        creditos = db.query(Credito).filter(Credito.cliente_id == item.cliente_id).all()
        for c in creditos:
            if c.dias_mora and c.dias_mora > 0:
                cliente = db.query(Cliente).filter(Cliente.id == item.cliente_id).first()
                result.append(
                    MoraItemOut(
                        id=str(item.id),
                        cliente_id=str(item.cliente_id),
                        cliente_nombre=f"{cliente.nombres} {cliente.apellidos}" if cliente else "---",
                        cod_cuenta_credito=c.cod_cuenta_credito,
                        dias_mora=c.dias_mora,
                        monto_vencido=c.saldo_total or 0,
                        tipo_gestion=item.tipo_gestion,
                    )
                )
    return sorted(result, key=lambda x: x.dias_mora, reverse=True)


@router.post("/accion")
def registrar_accion(data: AccionCobranzaCreate, asesor_id: str, db: Session = Depends(get_db)):
    accion = AccionCobranza(
        asesor_id=asesor_id,
        cliente_id=data.cliente_id,
        cod_cuenta_credito=data.cod_cuenta_credito,
        tipo_gestion=data.tipo_gestion,
        resultado=data.resultado,
        monto_pagado=data.monto_pagado,
        fecha_compromiso=data.fecha_compromiso,
        monto_compromiso=data.monto_compromiso,
        observaciones=data.observaciones,
        lat=data.lat,
        lng=data.lng,
    )
    db.add(accion)
    db.commit()
    return {"ok": True}
