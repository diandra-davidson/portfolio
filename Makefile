.PHONY: dev dev-down prod prod-down test health health-dev

# --- Dev ---

dev:
	docker compose -f docker-compose-dev.yml up -d

dev-down:
	docker compose -f docker-compose-dev.yml down

# --- Prod ---

prod:
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
		http://127.0.0.1 \
		https://scaling-computing-machine-g4665jxggqqfppjx-8000.app.github.dev/oauth/callback
