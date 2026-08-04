run:
    uv run fastapi dev src/main.py


check:
    uv run ruff check .
    uv run ruff format --check .


fix:
    uv run ruff check --fix .
    uv run ruff format .