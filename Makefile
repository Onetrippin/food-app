COMPOSE = docker compose

.PHONY: build up down logs restart ps shell migrate makemigrations createsuperuser collectstatic check

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

restart:
	$(COMPOSE) down
	$(COMPOSE) up --build -d

ps:
	$(COMPOSE) ps

shell:
	$(COMPOSE) exec web sh

migrate:
	$(COMPOSE) exec web python src/manage.py migrate

makemigrations:
	$(COMPOSE) exec web python src/manage.py makemigrations

createsuperuser:
	$(COMPOSE) exec web python src/manage.py createsuperuser

collectstatic:
	$(COMPOSE) exec web python src/manage.py collectstatic --noinput

check:
	$(COMPOSE) exec web python src/manage.py check
