SOURCES = pretf/pretf pretf-aws/pretf_aws tests

.PHONY: all
all:
	isort -rc $(SOURCES)
	black $(SOURCES)
	flake8 --ignore E501 $(SOURCES)
