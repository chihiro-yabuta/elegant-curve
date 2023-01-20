.PHONY: down

default:
	docker compose up -d
	mkdir archive input output
	cd archive && mkdir axis bspline result similar
down:
	docker compose down
	docker system prune -a