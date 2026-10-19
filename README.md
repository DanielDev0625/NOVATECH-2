# NovaTech – Plataforma de Operaciones Inteligentes para PyMEs

Trazabilidad, logística y eficiencia energética en una sola plataforma.

## Ejecutar
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Abrir http://127.0.0.1:8000 (el primer usuario registrado queda como administrador).

## Pruebas
```bash
cd backend
pytest
```