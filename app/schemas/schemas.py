from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    codigo_empleado: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    asesor: "AsesorOut"


class AsesorOut(BaseModel):
    id: str
    codigo_empleado: str
    nombres: str
    apellidos: str
    agencia_id: Optional[str] = None
    perfil: str

    class Config:
        from_attributes = True


class CarteraItemOut(BaseModel):
    id: str
    cliente_id: str
    cliente_nombre: str
    documento: str
    tipo_gestion: str
    prioridad: str
    score_prioridad: int
    monto_credito: Optional[float] = None
    estado_visita: str
    resultado_visita: Optional[str] = None
    observacion_visita: Optional[str] = None
    lat_visita: Optional[float] = None
    lng_visita: Optional[float] = None
    orden_manual: Optional[int] = None

    class Config:
        from_attributes = True


class CarteraFilter(BaseModel):
    tipo: Optional[str] = None
    busqueda: Optional[str] = None


class VisitaUpdate(BaseModel):
    estado_visita: str
    resultado_visita: Optional[str] = None
    observacion_visita: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class ClienteOut(BaseModel):
    id: str
    numero_documento: str
    nombres: str
    apellidos: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    tipo_negocio: Optional[str] = None
    nombre_negocio: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

    class Config:
        from_attributes = True


class FichaClienteOut(BaseModel):
    cliente: ClienteOut
    deuda_total: float = 0
    cuotas_al_dia: int = 0
    cuotas_mora: int = 0
    fecha_ultimo_pago: Optional[date] = None
    calificacion_sbs: Optional[str] = None


class PosicionCliente(BaseModel):
    deuda_total: float
    cuentas_vigentes: int
    cuentas_mora: int
    dias_mayor_mora: int
    fecha_ultimo_pago: Optional[date] = None


class SolicitudCreate(BaseModel):
    cliente_id: str
    monto_solicitado: float = Field(ge=500, le=150000)
    plazo_meses: int = Field(ge=3, le=60)
    tipo_negocio: Optional[str] = None
    nombre_negocio: Optional[str] = None
    destino_credito: Optional[str] = None
    moneda: str = "PEN"
    tipo_cuota: str = "mensual"
    garantia: Optional[str] = None
    firma_cliente_base64: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class SolicitudOut(BaseModel):
    id: str
    numero_expediente: Optional[str] = None
    cliente_id: str
    monto_solicitado: float
    estado: str
    created_at: datetime

    class Config:
        from_attributes = True


class SolicitudResumen(BaseModel):
    id: str
    cliente_nombre: str
    monto_solicitado: float
    estado: str
    dias_desde_envio: int
    analista_asignado: Optional[str] = None


class PreEvalRequest(BaseModel):
    numero_documento: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    tipo_negocio: str
    antiguedad_meses: int
    ingresos_estimados: float
    monto_solicitado: float


class PreEvalResponse(BaseModel):
    calificacion: str  # APTO / REVISAR / NO PROCEDE
    motivo: Optional[str] = None
    puntaje_interno: Optional[int] = None


class BuroRequest(BaseModel):
    numero_documento: str
    firma_consentimiento_base64: str


class BuroResponse(BaseModel):
    calificacion_sbs: str
    entidades_con_deuda: int
    deuda_total_pen: float
    mayor_deuda: float
    dias_mayor_mora: int
    en_lista_negra: bool
    motivo_bloqueo: Optional[str] = None
    interpretacion: Optional[str] = None


class AccionCobranzaCreate(BaseModel):
    cliente_id: str
    cod_cuenta_credito: str
    tipo_gestion: str  # visita / llamada / mensaje
    resultado: str
    monto_pagado: Optional[float] = None
    fecha_compromiso: Optional[date] = None
    monto_compromiso: Optional[float] = None
    observaciones: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class MoraItemOut(BaseModel):
    id: str
    cliente_id: str
    cliente_nombre: str
    cod_cuenta_credito: str
    dias_mora: int
    monto_vencido: float
    tipo_gestion: str
    ultimo_contacto: Optional[date] = None

    class Config:
        from_attributes = True


class AlertaOut(BaseModel):
    id: str
    cliente_id: str
    tipo_alerta: str
    mensaje: Optional[str] = None
    leida: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CampanaOut(BaseModel):
    id: str
    cliente_id: str
    cliente_nombre: str
    tipo: str
    monto_ofertado: Optional[float] = None
    fecha_vencimiento: Optional[date] = None

    class Config:
        from_attributes = True


class ClienteLoginRequest(BaseModel):
    username: str
    password: str


class ClienteLoginResponse(BaseModel):
    token: str
    cliente: ClienteOut


class OperacionCreate(BaseModel):
    cod_cuenta_origen: str
    cod_cuenta_destino: str
    tipo: str
    monto: float
    moneda: str = "PEN"


class OperacionOut(BaseModel):
    id: str
    tipo: str
    monto: float
    estado: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReporteProductividad(BaseModel):
    asesor_nombre: str
    enviadas: int
    aprobadas: int
    desembolsadas: int
    monto_total: float
    tasa_aprobacion: float
