.PHONY: neat
neat:
	isort -rc pretf tests
	black pretf tests
	flake8 pretf tests --ignore E501
