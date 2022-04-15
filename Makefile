

all:

.PHONY: test

test:
	export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
	nosetests  --with-coverage --cover-html --cover-erase --cover-html-dir=`pwd`/coverage --cover-package . -s -x

rpm:
	docker build -t nersc_sdn_rpm -f Dockerfile.rpmbuild .
