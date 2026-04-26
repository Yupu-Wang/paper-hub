PY := /opt/anaconda3/envs/paper-hub/bin/python

.PHONY: update build-shard build-manifest test serve

update:
	$(PY) -m scrapers.fetch_$(CONF) --year $(YEAR)
	$(PY) -m scrapers.build_shard --conf $(CONF) --year $(YEAR)
	$(PY) -m scrapers.build_manifest

build-shard:
	$(PY) -m scrapers.build_shard --conf $(CONF) --year $(YEAR)

build-manifest:
	$(PY) -m scrapers.build_manifest

test:
	$(PY) -m pytest tests/ -v

serve:
	@ln -sfn ../data web/data
	@echo "Visit http://localhost:8000"
	cd web && $(PY) -m http.server 8000
