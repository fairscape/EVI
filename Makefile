PYTHON ?= .venv/bin/python
export PYTHONPATH := scripts

.PHONY: venv test serialize site preview release check

venv:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements-dev.txt

test:
	$(PYTHON) -m pytest tests -q

serialize:
	$(PYTHON) scripts/serialize.py

site: serialize
	$(PYTHON) scripts/assemble_site.py

check: test site

preview: site
	@echo "Open http://127.0.0.1:8770/"
	python3 -m http.server 8770 --directory site

# Example: make release VERSION=1.7 COPY_FIGURE=1
release:
	@test -n "$(VERSION)" || (echo "Usage: make release VERSION=1.7"; exit 1)
	./scripts/release.sh $(VERSION) $(if $(COPY_FIGURE),--copy-figure,) $(if $(MODIFIED),--modified $(MODIFIED),)
