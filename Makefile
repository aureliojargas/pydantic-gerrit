gerrit_repo = ../gerrit

version = 3.12
version_package = v$(subst .,_,$(version))

version_docker_311 = 3.11.3
version_docker_312 = 3.12.0

endpoints = access accounts changes config documentation groups plugins projects
endpoint = groups

help:
	@echo "Choose one target."

# Gerrit sources repository

clone:
	@mkdir -p $(gerrit_repo)
	git clone https://gerrit.googlesource.com/gerrit $(gerrit_repo)
checkout:
	@git -C $(gerrit_repo) checkout --quiet stable-$(version)

# Docker

docker-run-3.11:
	docker run -p 8080:8080 -p 29418:29418 gerritcodereview/gerrit:$(version_docker_311)
docker-run-3.12:
	docker run -p 8080:8080 -p 29418:29418 gerritcodereview/gerrit:$(version_docker_312)

docker-fix:
	docker container prune -f
	docker image rm gerritcodereview/gerrit:$(version_docker_311)
	docker image rm gerritcodereview/gerrit:$(version_docker_312)

# List JSON entities from the REST API documentation

json-entities: checkout
	@cat $(gerrit_repo)/Documentation/rest-api-$(endpoint).txt | sed -n '1,/== JSON Entities/d; /^=== /s///p' | sort

# List models

models-implemented:
	@grep '^class.*BaseModelGerrit' src/pydantic_gerrit/$(version_package)/$(endpoint).py | cut -d ' ' -f 2 | cut -d '(' -f 1 | sort

# Conditions for a model to be considered tested:
# - .model_validate() was called
# - there's a comment `# indirect validation: ModelName`
# - there's a comment `# direct validation: ModelName`
models-tested:
	@temp_file=`mktemp`; \
	grep -o '[A-Za-z]*\.model_validate(' tests/test_*.py | cut -d . -f 1 > $$temp_file; \
	grep -o '# indirect validation: .*' tests/test_*.py | sed 's/.* //' >> $$temp_file; \
	grep -o '# direct validation: .*' tests/test_*.py | sed 's/.* //' >> $$temp_file; \
	sort $$temp_file | uniq

models-not-tested:
	@temp_file1=`mktemp`; \
	temp_file2=`mktemp`; \
	$(MAKE) --quiet models-implemented > $$temp_file1; \
	$(MAKE) --quiet models-tested > $$temp_file2; \
	comm -23 $$temp_file1 $$temp_file2

models-not-implemented:
	@$(MAKE) --quiet json-entities models-implemented | sort | uniq -u

# Repeat a target for all endpoints

%-all:
	@for ep in $(endpoints); do echo $$ep; $(MAKE) --quiet $* endpoint=$$ep | sed 's/^/  /'; done
