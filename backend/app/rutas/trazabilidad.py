# · Rutas de trazabilidad: lotes, etapas, consulta pública y certificado PDF.
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.esquemas.trazabilidad import EtapaIn, LoteIn
from app.modelos_db import Lote, get_db
from app.servicios import lotes as servicio
from app.servicios.certificado import generar_certificado
from app.servicios.seguridad import usuario_actual

router_publico = APIRouter(prefix="/api")
router = APIRouter(prefix="/api", dependencies=[Depends(usuario_actual)])


@router.post("/lotes")
def crear_lote(d: LoteIn, db: Session = Depends(get_db)):
    return servicio.lote_dict(servicio.crear_lote(db, d))


@router.get("/lotes")
def listar_lotes(db: Session = Depends(get_db)):
    return [servicio.lote_dict(l) for l in db.query(Lote).order_by(Lote.id.desc()).all()]


@router.get("/lotes/{codigo}")
def obtener_lote(codigo: str, db: Session = Depends(get_db)):
    return servicio.lote_dict(servicio.lote_por_codigo(db, codigo))


@router.patch("/etapas/{etapa_id}")
def actualizar_etapa(etapa_id: int, d: EtapaIn, db: Session = Depends(get_db)):
    return servicio.lote_dict(servicio.actualizar_etapa(db, etapa_id, d))


# · Consulta pública de un lote (es la página a la que lleva el código QR).
@router_publico.get("/publico/lotes/{codigo}")
def lote_publico(codigo: str, db: Session = Depends(get_db)):
    return servicio.lote_dict(servicio.lote_por_codigo(db, codigo))


@router_publico.get("/publico/lotes/{codigo}/certificado")
def certificado(codigo: str, request: Request, db: Session = Depends(get_db)):
    l = servicio.lote_por_codigo(db, codigo)
    # · La dirección del QR se arma con el dominio desde el que se hizo la petición.
    url = f"{str(request.base_url).rstrip('/')}/modulo.html?codigo={l.codigo}"
    pdf = generar_certificado(l, url)
    return StreamingResponse(pdf, media_type="application/pdf",
                             headers={"Content-Disposition": f'inline; filename="certificado_{l.codigo}.pdf"'})
