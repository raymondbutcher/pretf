SOURCES = pretf/pretf pretf.aws/pretf tests

.PHONY: all
all:
	isort -rc $(SOURCES)
	black $(SOURCES)
	flake8 --ignore E501 $(SOURCES)

clean:
	cd pretf; make clean
	cd pretf.aws; make clean
