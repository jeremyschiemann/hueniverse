build:
	poetry build

publish: build
	poetry publish

bumppatch:
	poetry run bump2version patch