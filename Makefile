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
	mypy -m pretf.api -m pretf.aws -m pretf.cli -m pretf.collections -m pretf.exceptions -m pretf.log -m pretf.parser -m pretf.render -m pretf.util -m pretf.variables -m pretf.workflow
	flake8 --ignore E501 $(SOURCES)
	python -m unittest discover tests

.PHONY: tidy
tidy:
	isort --recursive $(SOURCES)
	black $(SOURCES)
	cd examples; terraform fmt -recursive
