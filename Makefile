DC = docker compose
ARGS ?= -d

PROFILES_FRONTEND = --profile frontend
PROFILES_API = --profile api
PROFILES_INGEST = --profile ingestion
PROFILES_NTP = --profile ntp
PROFILES_CORE = --profile core
PROFILES_LOCALIZATION = --profile localization
PROFILES_DATASET = --profile dataset

dc-api:
	$(DC) \
	$(PROFILES_FRONTEND) \
	$(PROFILES_API) \
	up $(ARGS)

dc-ingest:
	$(DC) \
	$(PROFILES_INGEST) \
	$(PROFILES_NTP) \
	up $(ARGS)

dc-workers:
	$(DC) \
	$(PROFILES_CORE) \
	$(PROFILES_LOCALIZATION) \
	$(PROFILES_DATASET) \
	up $(ARGS)

dc-all:
	$(DC) \
	$(PROFILES_FRONTEND) \
	$(PROFILES_API) \
	$(PROFILES_INGEST) \
	$(PROFILES_NTP) \
	$(PROFILES_CORE) \
	$(PROFILES_LOCALIZATION) \
	$(PROFILES_DATASET) \
	up $(ARGS)

dc-down:
	$(DC) \
	$(PROFILES_FRONTEND) \
	$(PROFILES_API) \
	$(PROFILES_INGEST) \
	$(PROFILES_NTP) \
	$(PROFILES_CORE) \
	$(PROFILES_LOCALIZATION) \
	$(PROFILES_DATASET) \
	down --remove-orphans

dc-build:
	$(DC) \
	$(PROFILES_FRONTEND) \
	$(PROFILES_API) \
	$(PROFILES_INGEST) \
	$(PROFILES_NTP) \
	$(PROFILES_CORE) \
	$(PROFILES_LOCALIZATION) \
	$(PROFILES_DATASET) \
	build

dc-logs:
	$(DC) logs -f

help:
	@echo "Targets:"
	@echo "  make dc-api       -> frontend + api + localization"
	@echo "  make dc-ingest    -> ingestion + ntp"
	@echo "  make dc-workers   -> pipeline workers"
	@echo "  make dc-all       -> everything"
	@echo ""
	@echo "Optional:"
	@echo "  ARGS='--build' or '--scale service=2'"
