.PHONY: lint
lint: flake8 mypy check_import_order check_format

.PHONY: test
test: pytest

.PHONY: format
format: isort black

.PHONY: isort
isort:
	isort template_analysis tests

.PHONY: black
black:
	black template_analysis tests

.PHONY: flake8
flake8:
	flake8 template_analysis tests

.PHONY: mypy
mypy:
	mypy template_analysis tests

.PHONY: check_import_order
check_import_order:
	isort --check-only --diff template_analysis tests

.PHONY: check_format
check_format:
	black --check template_analysis tests

.PHONY: pytest
pytest:
	pytest --cov=template_analysis tests --doctest-modules --cov-report=xml

.PHONY: build
build:
	python3 -m build .

.PHONY: clean
clean:
	rm -rf *.egg-info dist
