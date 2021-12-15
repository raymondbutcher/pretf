FORMAT_SOURCES = pretf/pretf pretf.aws/pretf tests
ALL_SOURCES = $(FORMAT_SOURCES) examples

.PHONY: all
all: tidy test

.PHONY: clean
clean:
	cd pretf; make clean
	cd pretf.aws; make clean

.PHONY: docs
docs:
	mkdocs serve

.PHONY: test
test:
	mypy $(shell python -c 'import pathlib; print(" ".join(sorted(f"-m pretf.{p.stem}" for p in pathlib.Path().glob("pretf*/pretf/*.py"))))')
	flake8 --ignore E501,W503 $(ALL_SOURCES)
	pytest -v tests

.PHONY: tidy
tidy:
	isort --float-to-top --profile black $(ALL_SOURCES)
	black $(FORMAT_SOURCES)
	cd examples; terraform fmt -recursive

.PHONY: testall
testall: tidy test
	pytest -v examples
