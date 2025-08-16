# VidaPlus - Sistema de Gestão Hospitalar e de Serviços de Saúde (SGHSS)

Back-end do **SGHSS Sistema de Gestão Hospitalar e de Serviços de Saúde** em **Flask**.
Para a trilha de formação Back-End do curso de Análise e Desenvolvimento de Sistemas  


---

## 🔧 Stack
- Python **3.13.7**
- Flask · Flask-Smorest (OpenAPI) · Flask-JWT-Extended · Flask-Migrate/Alembic
- SQLAlchemy 2.x · marshmallow
- CORS · Flask-Limiter (rate limit) · uploads (Werkzeug)
- SQLite (dev) — compatível com Postgres/MySQL

---

## 📁 Estrutura do projeto

```
PROJETO ELETIVO BACK END/
├─ __pycache__/
├─ .venv/
├─ instance/
├─ migrations/
├─ models/
├─ resources/
├─ schemas/
├─ utils/
├─ app.py
├─ config.py
├─ extensions.py
├─ README.md
├─ requirements.txt
├─ SGHSS.postman_collection.json
└─ wsgi.py
```

> **Obs.:** `uploads/` é criado em runtime (não versionado). Recomendo `.gitignore` para `.venv/`, `__pycache__/`, `uploads/`, `instance/`, `.env`, `*.sqlite` etc.

---

## 🚀 Quickstart (Windows PowerShell)

### 1) Clonar, venv e deps
```powershell
git clone https://github.com/Pacienza/Projeto-Eletivo-Back-End.git
cd Projeto-Eletivo-Back-End

py -3.13 -m venv .venv
. .\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) `.env` (na raiz)
```env
FLASK_ENV=development
SECRET_KEY=dev-secret
JWT_SECRET_KEY=dev-jwt-secret
SQLALCHEMY_DATABASE_URI=sqlite:///sghss.db
SQLALCHEMY_TRACK_MODIFICATIONS=False
CORS_ORIGINS=*
UPLOAD_DIR=uploads
TELE_BASE_URL=https://tele.local/s
# Opcional: RATELIMIT_STORAGE_URL=redis://localhost:6379/0
```

### 3) Banco (migrações)
```powershell
flask --app app:create_app db upgrade
```

### 4) Seed do admin
```powershell
flask --app app:create_app seed-admin --email admin@local --senha 123456
```

### 5) Rodar
```powershell
flask --app app:create_app run
# http://localhost:5000
```

### 6) Swagger
Abra **http://localhost:5000/docs/**

---

## 🔐 JWT & RBAC
- **Roles:** `paciente`, `profissional`, `admin`.
- Token inclui as claims: `role`, `email`, `paciente_id`, `profissional_id`.
- `identity` no token é **string**: use `get_jwt_identity()` e converte para `int` quando você precisar.

---

## 🧾 Auditoria
Tabela `auditoria` (quem, o quê, onde, quando, IP).  
`utils.audit.audit(acao, recurso, referencia_id, detalhes)` é chamado em login, criação/cancelamento de consulta, finalizar tele, prontuário/prescrição, admitir/alta etc.

---

## 📦 Módulos/Rotas (visão geral)
- **/auth**: `login`, `register` (admin), `me`
- **/public**: auto-cadastro de paciente
- **/pacientes**, **/profissionais**
- **/agendas**: slots
- **/consultas**: agendar/listar/cancelar + **notificações**
- **/teleconsultas**: criar/listar/finalizar/cancelar + **anexos** (upload/lista/download)
- **/prontuarios** e **/prescricoes**
- **/internacoes**: admitir/atualizar/alta
- **/relatorios**: consultas/tele por período; internações/tempo médio
- **/me/historico**: histórico completo do paciente logado

---

## 🧪 Postman (E2E)
- Coleção: **`SGHSS.postman_collection.json`** (na raiz).
- Ambiente: **`SGHSS.postman_enviroment.json`**  
- Fluxo de testes da API em ordem:
  1. **Login ADMIN** → criar paciente/profissional → registrar usuários
  2. **Login PROF** → criar slot(Vaga Disponivel)
  3. **Login PAC** → agendar **e** cancelar consulta
  4. **Tele**: criar → upload anexo → finalizar (gera prontuário)
  5. **Prescrição** (PROF)
  6. **Internação**: admitir → alta
  7. **Relatórios** (ADMIN)
  8. **/me/historico** + **/notificacoes** (PAC)

---
