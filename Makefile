.PHONY: init clean build up down

init:
	mkdir -p src tests/unit tests/integration templates static data
	touch src/__init__.py
	touch tests/__init__.py
	touch tests/unit/__init__.py
	touch tests/integration/__init__.py

clean:
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
	rm -f data/*.json

build:
	docker build -t splitbill:latest .

up:
	docker-compose up -d

down:
	docker-compose down