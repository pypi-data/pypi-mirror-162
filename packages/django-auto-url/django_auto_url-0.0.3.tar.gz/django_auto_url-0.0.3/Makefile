# simple makefile to simplify repetetive build env management tasks under posix

# caution: testing won't work on windows, see README
VERSION_FILE:=VERSION
VERSION:=$(strip $(shell cat ${VERSION_FILE}))
PYPIVERSION:=$(subst _,.,$(VERSION))
pypidist:=dist/django-auto-url-$(PYPIVERSION).tar.gz

ifeq ($(findstring dev,$(VERSION)), dev)
	export TWINE_REPOSITORY_URL=https://test.pypi.org/legacy/
	ifeq ($(shell echo -n $(PYPIVERSION) | tail -c 1), v)
		PYPIVERSION:=$(PYPIVERSION)0
	endif
	ISDEV:=1
else
	ISDEV:=0
endif

flake:
	@if command -v flake8 > /dev/null; then \
		echo "Running flake8"; \
		flake8 --count django_auto_url; \
	else \
		echo "flake8 not found, please install it!"; \
		exit 1; \
	fi;
	@echo "flake8 passed"

pydocstyle:
	@pydocstyle django_auto_url

code_quality:
	docker run --interactive --tty --rm --env \
	CODECLIMATE_CODE="$(CURDIR)" --volume "$(CURDIR)":/code \
	--volume /var/run/docker.sock:/var/run/docker.sock \
	--volume /tmp/cc:/tmp/cc  codeclimate/codeclimate analyze

update_deps:
	pip install -U -r requirements.txt

COPYRIGHT_CMD ?= docker run --rm --volume `pwd`:$(COPYRIGHT_OUTPUT_DIR) osterman/copyright-header:latest
COPYRIGHT_LICENSE ?= GPL3
COPYRIGHT_HOLDER ?= Thomas Hartmann <thomas.hartmann@th-ht.de>
COPYRIGHT_YEAR ?= 2019
COPYRIGHT_SOFTWARE ?= django_auto_url
COPYRIGHT_SOFTWARE_DESCRIPTION ?= Automagic URLs for Django
COPYRIGHT_OUTPUT_DIR ?= /usr/src
COPYRIGHT_WORD_WRAP ?= 75
COPYRIGHT_PATHS ?= django_auto_url

remove-copyright:
	$(COPYRIGHT_CMD) \
	  --license $(COPYRIGHT_LICENSE)  \
	  --remove-path $(COPYRIGHT_PATHS) \
	  --guess-extension \
	  --copyright-holder '$(COPYRIGHT_HOLDER)' \
	  --copyright-software '$(COPYRIGHT_SOFTWARE)' \
	  --copyright-software-description '$(COPYRIGHT_SOFTWARE_DESCRIPTION)' \
	  --copyright-year $(COPYRIGHT_YEAR) \
	  --word-wrap $(COPYRIGHT_WORD_WRAP) \
	  --output-dir $(COPYRIGHT_OUTPUT_DIR)

add-copyright:
	$(COPYRIGHT_CMD) \
	  --license $(COPYRIGHT_LICENSE)  \
	  --add-path $(COPYRIGHT_PATHS) \
	  --guess-extension \
	  --copyright-holder '$(COPYRIGHT_HOLDER)' \
	  --copyright-software '$(COPYRIGHT_SOFTWARE)' \
	  --copyright-software-description '$(COPYRIGHT_SOFTWARE_DESCRIPTION)' \
	  --copyright-year $(COPYRIGHT_YEAR) \
	  --word-wrap $(COPYRIGHT_WORD_WRAP) \
--output-dir $(COPYRIGHT_OUTPUT_DIR)

build-doc:
	cd doc; make clean; make html

autobuild-doc:
	sphinx-autobuild doc/source doc/build

pep:
	@$(MAKE) -k flake pydocstyle

clean-dist:
	rm -rf dist
	rm -rf django_auto_url.egg-info

$(pypidist):
	python setup.py sdist

make-dist: $(pypidist)

upload-dist: make-dist
	twine upload dist/django_auto_url-$(PYPIVERSION).tar.gz
ifneq ($(findstring dev,$(VERSION)), dev)
	git tag -a v$(VERSION) -m "version $(VERSION)"
	git push origin v$(VERSION)
endif