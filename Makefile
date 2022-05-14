release:
	standard-version
	git push --follow-tags origin master

test:
	python -m pytest
