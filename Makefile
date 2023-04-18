check:
	flake8 .
	black . --preview --check
	mypy .

test: check
	coverage run -m pytest
	coverage report -m --skip-covered

