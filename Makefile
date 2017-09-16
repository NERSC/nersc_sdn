

all:

.PHONY: test

test:
	nosetests  --with-coverage --cover-html --cover-html-dir=`pwd`/coverage --cover-package . -s -x
