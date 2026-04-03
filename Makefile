# ════════════════════════════════════════
# Family Wallet — команди розробки
# ════════════════════════════════════════

.PHONY: install lint lint-fix format format-check run dev

# ── Встановлення залежностей ─────────────
install:
	cd frontend && npm install
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

# ── Лінтери ──────────────────────────────
lint: lint-frontend lint-backend

lint-frontend:
	cd frontend && npx eslint src/

lint-backend:
	cd backend && . .venv/bin/activate && ruff check app/

lint-fix: lint-fix-frontend lint-fix-backend

lint-fix-frontend:
	cd frontend && npx eslint src/ --fix

lint-fix-backend:
	cd backend && . .venv/bin/activate && ruff check app/ --fix

# ── Форматування ────────────────────────
format: format-frontend format-backend

format-frontend:
	cd frontend && npx prettier --write src/

format-backend:
	cd backend && . .venv/bin/activate && ruff format app/

format-check: format-check-frontend format-check-backend

format-check-frontend:
	cd frontend && npx prettier --check src/

format-check-backend:
	cd backend && . .venv/bin/activate && ruff format --check app/

# ── Перевірка якості (lint + format) ─────
check: lint format-check

# ── Запуск ───────────────────────────────
dev:
	docker-compose up --build

dev-frontend:
	cd frontend && npm run dev

dev-backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000
