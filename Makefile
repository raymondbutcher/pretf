$(eval NAME := $(shell python setup.py --name))
$(eval PY_NAME := $(shell python setup.py --name | sed 's/-/_/g'))
$(eval VERSION := $(shell python setup.py --version))

SDIST = dist/$(NAME)-$(VERSION).tar.gz
WHEEL = dist/$(PY_NAME)-$(VERSION)-py3-none-any.whl

SOURCES = pretf tests setup.py

.PHONY: all
all:
	isort -rc $(SOURCES)
	black $(SOURCES)
	flake8 --ignore E501 $(SOURCES)

.PHONY: build
build: clean $(SDIST) $(WHEEL)

.PHONY: clean
clean:
	rm -rf build dist *.egg-info

.PHONY: upload
upload: $(SDIST) $(WHEEL)
	twine upload $(SDIST) $(WHEEL)

$(SDIST):
	python setup.py sdist

$(WHEEL):
	python setup.py bdist_wheel
