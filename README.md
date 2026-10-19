# SmartOps – Operaciones Inteligentes para PyMEs Industriales

Producción y trazabilidad, logística y distribución, costos y eficiencia energética, y reportes en una sola plataforma.

Backend FastAPI + frontend HTML/JS (carpeta `backend/public`) + base de datos PostgreSQL (Neon).

## Ejecutar en local
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # Linux/Mac: cp .env.example .env  (y completa DATABASE_URL y SECRET_KEY)
uvicorn app.main:app --reload
```
Abrir http://127.0.0.1:8000 (el primer usuario registrado queda como administrador).
Sin `DATABASE_URL` usa un SQLite local (`novatech.db`) para pruebas.

## Pruebas
```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

## Desplegar en Vercel (con Neon)
1. En Vercel: **Add New → Project** e importa este repositorio.
2. **Root Directory:** `backend` (Framework Preset: *Other*).
3. En **Environment Variables** agrega:
   - `DATABASE_URL`: la cadena de Neon (usa la *pooled connection*, con `?sslmode=require`).
   - `SECRET_KEY`: una clave larga y aleatoria (`python -c "import secrets; print(secrets.token_urlsafe(48))"`).
   - Opcionales: `UTC_OFFSET_HORAS` (por defecto `-5`), `FACTOR_EMISION_KWH`, `FACTOR_EMISION_KM`.
4. **Deploy**. La API queda en `/api/*` y el frontend (`backend/public`) se sirve desde la raíz.

Las tablas que falten se crean solas en el primer arranque; las existentes no se modifican.
