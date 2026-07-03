from datetime import date
from fastapi import APIRouter
from app.schemas import PreEvalRequest, PreEvalResponse

router = APIRouter(prefix="/pre-evaluar", tags=["Pre-evaluacion"])


@router.post("", response_model=PreEvalResponse)
def pre_evaluar(data: PreEvalRequest):
    edad = date.today().year - data.fecha_nacimiento.year
    if edad < 18 or edad > 75:
        return PreEvalResponse(calificacion="NO PROCEDE", motivo="Edad fuera del rango (18-75)")

    if data.antiguedad_meses < 6:
        return PreEvalResponse(calificacion="REVISAR", motivo="Antiguedad del negocio menor a 6 meses")

    if data.ingresos_estimados <= 0:
        return PreEvalResponse(calificacion="NO PROCEDE", motivo="Ingresos no registrados")

    if data.monto_solicitado > data.ingresos_estimados * 12:
        return PreEvalResponse(calificacion="REVISAR", motivo="Monto solicitado excede capacidad de pago")

    puntaje = min(100, int(data.ingresos_estimados / data.monto_solicitado * 50 + data.antiguedad_meses))
    if puntaje >= 60:
        return PreEvalResponse(calificacion="APTO", puntaje_interno=puntaje)
    elif puntaje >= 35:
        return PreEvalResponse(calificacion="REVISAR", motivo="Puntaje interno insuficiente", puntaje_interno=puntaje)
    else:
        return PreEvalResponse(calificacion="NO PROCEDE", motivo="Bajo puntaje crediticio", puntaje_interno=puntaje)
