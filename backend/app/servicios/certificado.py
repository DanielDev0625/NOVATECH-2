# · Genera el certificado de trazabilidad en PDF, con un código QR que lleva al lote.
import io

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.modelos_db import Lote
from app.servicios.lotes import estado_lote


def generar_certificado(l: Lote, url: str) -> io.BytesIO:
    # · Imagen QR en memoria con la dirección pública del lote.
    qr = io.BytesIO()
    qrcode.make(url).save(qr, format="PNG")
    qr.seek(0)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # · Encabezado.
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, h - 70, "Certificado de trazabilidad")
    c.setFont("Helvetica", 11)
    c.drawString(50, h - 90, "SmartOps - Operaciones Inteligentes para PyMEs Industriales")

    # · Datos principales del lote.
    y = h - 135
    for t, v in [("Lote", l.codigo), ("Producto", l.producto),
                 ("Cantidad", f"{l.cantidad:g} {l.unidad}"), ("Responsable", l.responsable or "-"),
                 ("Creado", f"{l.creado_en:%d/%m/%Y %H:%M}"), ("Estado", estado_lote(l))]:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"{t}:")
        c.setFont("Helvetica", 11)
        c.drawString(150, y, str(v))
        y -= 20

    # · Historial de etapas.
    y -= 10
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Historial de etapas")
    y -= 22
    for e in l.etapas:
        est = f"completada {e.fecha_real:%d/%m/%Y}" if e.completada and e.fecha_real else "pendiente"
        cal = "calidad OK" if e.control_calidad else "sin control de calidad"
        c.setFont("Helvetica", 10)
        c.drawString(55, y, f"- {e.nombre}: {est} | {cal} | resp.: {e.responsable or '-'}")
        y -= 16

    # · Código QR en la esquina inferior derecha.
    c.drawImage(ImageReader(qr), w - 190, 60, 130, 130)
    c.setFont("Helvetica", 8)
    c.drawString(w - 190, 50, "Escanee para consultar el lote")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf
