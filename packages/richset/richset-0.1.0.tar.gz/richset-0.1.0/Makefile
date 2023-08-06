.PHONY: lint
lint: flake8 mypy check_import_order check_format

.PHONY: test
test: pytest

.PHONY: format
format: isort black

.PHONY: isort
isort:
	isort richset tests

.PHONY: black
black:
	black richset tests

.PHONY: flake8
flake8:
	flake8 richset tests

.PHONY: mypy
mypy:
	mypy richset tests

.PHONY: check_import_order
check_import_order:
	isort --check-only --diff richset tests

.PHONY: check_format
check_format:
	black --check richset tests

.PHONY: pytest
pytest:
	pytest --cov=richset tests --doctest-modules --cov-report=xml

.PHONY: build
build:
	python3 -m build .

.PHONY: clean
clean:
	rm -rf *.egg-info dist
