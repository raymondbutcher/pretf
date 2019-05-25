.PHONY: neat
neat:
	black pretf
	flake8 pretf --ignore E501
