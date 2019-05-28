SOURCES = pretf/pretf pretf.aws/pretf tests

.PHONY: all
all:
	isort --recursive $(SOURCES)
	black $(SOURCES)
	flake8 --ignore E501 $(SOURCES)
	cd tests; terraform fmt -recursive

clean:
	cd pretf; make clean
	cd pretf.aws; make clean
