SOURCES = pretf/pretf pretf.aws/pretf examples

.PHONY: all
all:
	isort --recursive $(SOURCES)
	black $(SOURCES)
	flake8 --ignore E501 $(SOURCES)
	cd examples; terraform fmt -recursive

clean:
	cd pretf; make clean
	cd pretf.aws; make clean
