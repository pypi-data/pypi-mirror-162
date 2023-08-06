# Find poetry toml file, package version and name and __version__.py file
TOMLFILE = $(shell find ./ -maxdepth 1 -name '*.toml')
VERSIONTOML = $(shell grep 'version' $(TOMLFILE) | sed 's/^.*= //')
PKGNAME = $(shell grep 'name' $(TOMLFILE) | sed 's/^.*= //')
VERSIONFILE = $(shell find ./$(PKGNAME) -maxdepth 1 -name '__version__.py')
INCLUDES := $(shell find ./vignette_src/ -maxdepth 1 -name '*.Rmd')

.PHONY: default
default: final

# Check if a toml and __version__.py files are present.
check:
	@echo "Checking poetry toml file...\n"
	@if [ -z $(TOMLFILE) ]; then echo "ERROR: No '.toml' can be found\n"; \
        exit 1; fi
	@echo "Checking pkg __version__.py file...\n"
	@if [ -z $(VERSIONFILE) ]; \
        then echo "ERROR: No '__version__.py' can be found in './$(PKGNAME)'\n"; \
        exit 1; fi
	@echo "...Finished\n"
	poetry run pip3 install jrpytests
	poetry run python3 -c "import jrpytests; jrpytests.checkvignettespdffiles()"
	poetry run python3 -c "import jrpytests; jrpytests.runpytests()"
	poetry run python3 -c "import jrpytests; jrpytests.runflake8pythonfiles()"
	poetry run python3 -c "import jrpytests; jrpytests.runflake8rmdpychunks()"

# Match version in toml and __version__.py.
version: check
	@echo "Matching version between toml and __version__.py...\n"
	@if [ -z $(VERSIONTOML) ]; \
        then echo "ERROR: No 'version' can be found in $(TOMLFILE) \n"; \
        exit 1; else sed -i.bak 's/.*__version__.*/__version__ = $(VERSIONTOML)/' $(VERSIONFILE);\
        fi
	@if [ -f $(VERSIONFILE).bak ]; then rm $(VERSIONFILE).bak; fi
	@echo "...Finished\n"

final: 
	Rscript -e 'jrNotes2::build_python_vignettes()'

# Install package and build distribution
build:  ./pyproject.toml
	poetry update
	poetry install
	poetry build

# Publish on PyPi
publish: build dist/*
	poetry publish
