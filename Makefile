.PHONY: install doctor fetch build serve eval ablation test acceptance offline-demo

install:
	pip install -e ".[dev]"

doctor:
	amlrag doctor

fetch:
	amlrag fetch

build:
	amlrag build

serve:
	amlrag serve

eval:
	amlrag eval

ablation:
	amlrag eval --preset all

test:
	pytest

acceptance:
	AMLRAG_RUN_EVAL=1 pytest tests/acceptance -v

# UI work without Ollama (hash embedder + stub generator; rebuild with `make build` afterwards)
offline-demo:
	amlrag build --offline && amlrag serve --offline
