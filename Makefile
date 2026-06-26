# RAG Studio Pro — developer convenience commands.

.PHONY: help up up-build down logs ps clean health setup

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Create .env from .env.example if missing
	@test -f .env || (cp .env.example .env && echo "Created .env from .env.example")

up: setup ## Start the full local stack
	docker compose up

up-build: setup ## Rebuild images and start the stack
	docker compose up --build

down: ## Stop the stack
	docker compose down

logs: ## Tail logs for all services
	docker compose logs -f

ps: ## List running services
	docker compose ps

health: ## Hit the backend health endpoint
	@curl -fsS http://localhost:8000/health && echo

clean: ## Stop the stack and remove volumes (DESTRUCTIVE)
	docker compose down -v
