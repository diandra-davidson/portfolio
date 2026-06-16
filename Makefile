.PHONY: dev dev-down prod prod-down test health health-dev

# --- Dev ---
# Unset stale shell exports that would override .env payload key values

dev:
	env -u AWS_SECRETSMANAGER_SERVICE_NAME -u AWS_SECRETSMANAGER_FLASK_SERVICE_NAME \
		docker compose -f docker-compose-dev.yml up -d --build

dev-down:
	docker compose -f docker-compose-dev.yml down

# --- Prod ---
# Unset stale shell exports that would override .env payload key values

prod:
	env -u AWS_SECRETSMANAGER_SERVICE_NAME -u AWS_SECRETSMANAGER_FLASK_SERVICE_NAME \
		docker compose -f docker-compose.yml up -d --build

prod-down:
	docker compose -f docker-compose.yml down

# --- Test ---

test:
	python -m pytest

# --- Health checks ---

health:
	./tools/prod_health_check.sh https://portfolio.diandrad.dev

health-dev:
	./tools/prod_health_check.sh \
		"$${BASE_URL_DEV:-http://127.0.0.1}" \
		"$${CALLBACK_URL_DEV:-http://127.0.0.1/oauth/callback}"
