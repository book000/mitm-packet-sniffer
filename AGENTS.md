# AGENTS.md

Guidance for AI coding agents and contributors. `CLAUDE.md` imports this file, and `.github/copilot-instructions.md` adds the review checklist.

## Language

- All deliverables are written in **English**: commit messages, PR/Issue titles and bodies, review comments, code comments and docstrings, and documentation (`README.md`, `AGENTS.md`, etc.).
- Exceptions (keep as is): quotations, technical identifiers, generated files, and external source text.
- Runtime messages (logs, errors) are English.
- Do not rewrite Git history to change the language of past commits.

## Overview

A mitmproxy addon (`mitmproxy-addon/main.py`) that stores every HTTP(S) request/response pair it proxies in MySQL, run with Docker Compose. See `README.md` for setup and usage.

## Commands

```bash
docker compose up -d --build                  # mysql + mitmproxy + phpMyAdmin
docker compose -f compose-db.yaml up -d       # MySQL + phpMyAdmin only
docker compose -f compose-export.yaml up      # dump the live schema to database/schema/ (mysqldef --export)
docker compose -f compose-import.yaml up      # apply database/schema/*.sql to the DB (joins the project's default network, so the database must be running)
```

There is no test suite, linter or build script. CI (`.github/workflows/docker.yml`) builds the image with the reusable workflow from `book000/templates` and runs a smoke test that starts `docker compose up` and fails if the `mitmproxy` container is not running or has restarted. Fork PRs need manual approval of the `fork-pr-build` Environment.

## Structure

- `mitmproxy-addon/`: `main.py` (`Database` and `Addon` classes), `entrypoint.sh` (runs `mitmdump -s /app/main.py --set confdir=/data/mitmproxy-conf/`), `Dockerfile`, `requirements.txt`. Connection settings come from `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` and optional `DB_PORT`.
- `database/`: `schema/mitm-packet-sniffer.sql` (source of truth for the schema; also mounted into the MySQL init directory by `compose.yaml`) and a `mysqldef` (sqldef) wrapper image used by the export/import compose files.
- `compose*.yaml`: see Commands.

## Conventions

- Database access is asynchronous (`aiomysql`); pass values to SQL as parameters (`%s` placeholders), never by string concatenation.
- Binary bodies are stored as Base64; the content type is classified as `BINARY` / `JSON` / `XML` / `TEXT` (or `NULL` when there is no content). Keep this consistent with the `*_content_type` columns when changing the classification.
- Intercepted traffic can contain personal data and credentials: never log bodies or headers, and never commit anything from `data/` (mitmproxy CA certificate and key, git-ignored) or `mysql/`.
- Deliberate choices, not defects: the DB credentials in `compose*.yaml` are development defaults; `entrypoint.sh` does not set `tls_version_client_min` because explicitly setting it crashes mitmproxy at startup with some OpenSSL builds; the 30 second sleep after an abnormal `mitmdump` exit throttles restarts caused by `restart: always`.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/); branches follow [Conventional Branch](https://conventional-branch.github.io) short form (`feat/...`, `fix/...`).
- Do not commit to Renovate PRs. Never commit secrets.
