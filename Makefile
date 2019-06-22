SOURCES = pretf/pretf pretf.aws/pretf examples tests

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
	flake8 --ignore E501 $(SOURCES)
	pytest -v tests

.PHONY: tidy
tidy:
	isort --recursive $(SOURCES)
	black $(SOURCES)
	cd examples; terraform fmt -recursive

.PHONY: testall
testall: tidy test
	pytest -v examples
