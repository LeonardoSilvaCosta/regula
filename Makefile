.PHONY: build up down logs gen-types cli-test

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

gen-types:
	cd frontend && npm run gen:types

cli-test:
	docker compose run --rm --no-deps --entrypoint python backend main.py --help
