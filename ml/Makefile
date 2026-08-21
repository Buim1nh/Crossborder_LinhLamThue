# Pipeline SUBSCRIPTION — chay tu thu muc goc repo: make -f ml/Makefile <target>
PY ?= .venv/bin/python
CFG ?= ml/config.yaml
DATA ?=

.PHONY: help setup audit train evaluate predict promote versions drift test lint clean docker-build docker-train all

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup:          ## tao venv + cai dependency
	python3 -m venv .venv && $(PY) -m pip install -q --upgrade pip && \
	$(PY) -m pip install -q -r ml/requirements.txt pytest

audit:          ## kiem tra ro ri nhan
	$(PY) -m ml.cli --config $(CFG) audit --out ml/artifacts/leakage_report.json

train:          ## train + cross-validate + dong goi vao registry
	$(PY) -m ml.cli --config $(CFG) train

train-promote:  ## train roi promote luon neu qua cong chat luong
	$(PY) -m ml.cli --config $(CFG) train --promote

evaluate:       ## cham model current tren DATA=<file.csv>
	$(PY) -m ml.cli --config $(CFG) evaluate --data $(DATA)

predict:        ## du doan cho DATA=<file.csv>
	$(PY) -m ml.cli --config $(CFG) predict --input $(DATA) --output ml/artifacts/predictions.csv

promote:        ## promote phien ban moi nhat
	$(PY) -m ml.cli --config $(CFG) promote

versions:       ## liet ke registry
	$(PY) -m ml.cli --config $(CFG) versions

drift:          ## do lech phan phoi cho DATA=<file.csv>
	$(PY) -m ml.cli --config $(CFG) drift --data $(DATA)

test:           ## chay unit test
	$(PY) -m pytest ml/tests -q

clean:          ## xoa file tam
	rm -rf ml/artifacts/predictions*.csv ml/**/__pycache__ .pytest_cache

docker-build:   ## build image cho pipeline
	docker build -f ml/Dockerfile -t wealify-ml:latest .

docker-train:   ## train trong container, ghi registry ra host
	docker run --rm -v $(PWD)/ml/registry:/app/ml/registry \
		-v $(PWD)/subscription_labels.csv:/app/subscription_labels.csv:ro \
		wealify-ml:latest train

all: test audit train ## kiem tra day du roi train
