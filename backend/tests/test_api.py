import os

os.environ["DATABASE_URL"] = "sqlite:///./test_novatech.db"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_flujo_basico():
    with TestClient(app) as c:
        r = c.post("/api/auth/registro", json={"nombre": "Test", "email": "t@t.com", "password": "123456"})
        assert r.status_code in (200, 400)
        r = c.post("/api/auth/login", json={"email": "t@t.com", "password": "123456"})
        assert r.status_code == 200
        h = {"Authorization": f"Bearer {r.json()['token']}"}

        assert c.get("/api/lotes").status_code == 401
        lote = c.post("/api/lotes", json={"producto": "Café", "cantidad": 100}, headers=h).json()
        assert len(lote["etapas"]) == 3

        pub = c.get(f"/api/publico/lotes/{lote['codigo']}")
        assert pub.status_code == 200
        pdf = c.get(f"/api/publico/lotes/{lote['codigo']}/certificado")
        assert pdf.headers["content-type"] == "application/pdf"