# · Rutas del panel general y de los reportes.
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.modelos_db import get_db
from app.servicios import reportes as servicio
from app.servicios.alertas import alertas_consumo, alertas_lotes
from app.servicios.seguridad import usuario_actual

router = APIRouter(prefix="/api", dependencies=[Depends(usuario_actual)])


@router.get("/panel/resumen")
def panel_resumen(db: Session = Depends(get_db)):
    return servicio.resumen_panel(db)


@router.get("/reportes/huella")
def huella(db: Session = Depends(get_db)):
    return servicio.huella_carbono(db)


@router.get("/reportes/alertas")
def reporte_alertas(db: Session = Depends(get_db)):
    return alertas_lotes(db) + alertas_consumo(db)
