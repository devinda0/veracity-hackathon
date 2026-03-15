.PHONY: up down logs ps restart shell-mongo shell-redis shell-postgres

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

restart:
	docker compose down
	docker compose up -d

shell-mongo:
	docker compose exec mongo mongosh -u $${MONGO_INITDB_ROOT_USERNAME:-admin} -p $${MONGO_INITDB_ROOT_PASSWORD:-admin123} --authenticationDatabase admin

shell-redis:
	docker compose exec redis redis-cli

shell-postgres:
	docker compose exec postgres psql -U $${POSTGRES_USER:-postgres} -d $${POSTGRES_DB:-vector_agents}

