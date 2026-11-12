# mitm-packet-sniffer

A [mitmproxy](https://mitmproxy.org/) addon that records every HTTP(S) request/response pair passing through the proxy into a MySQL database. It runs as a Docker Compose stack of MySQL, mitmproxy (with the addon) and phpMyAdmin.

Only use it to inspect traffic you are entitled to inspect. Stored requests and responses contain whatever the clients sent, including credentials and personal data.

## Setup

Requirements: Docker with the Compose plugin.

```bash
docker compose up -d --build
```

This starts:

| Service | Description | Host port |
|---|---|---|
| `mysql` | MySQL. The schema in `database/schema/` is loaded on first start. Data is kept in `./mysql`. | none |
| `mitmproxy` | `mitmdump` with `mitmproxy-addon/main.py`. State (including the CA certificate) is kept in `./data`. | `10000` (proxy, `8080` in the container) |
| `phpmyadmin` | Web UI for the database, pre-configured to log in as the application user. | `8080` |

The database credentials in `compose.yaml` (`mitm-packet-sniffer` / `mitm-packet-sniffer-password`, root password `rootPassword`) are development defaults. Change them before exposing the stack to anything untrusted.

### Intercepting HTTPS

1. Start the stack once so mitmproxy generates its CA in `./data/mitmproxy-conf/` (for example `mitmproxy-ca-cert.pem`).
2. Install and trust that certificate on the client device.
3. Point the client's HTTP/HTTPS proxy at `<docker-host>:10000`.

Keep `./data/mitmproxy-conf/` private: it holds the CA private key. The directory is git-ignored.

## Usage

Once a client uses the proxy, each response is stored as one row in the `responses` table. Browse it in phpMyAdmin at <http://localhost:8080/> or query it with any MySQL client.

### What is stored

`responses` has one row per HTTP response, with the request side (`host`, `port`, `method`, `scheme`, `authority`, `path`, `query`, `request_headers`, `request_content`, `http_version`) and the response side (`status_code`, `response_headers`, `response_content`), plus `created_at`. Details:

- `path` has the query string removed; `path_hash` is the MD5 of `path`; `query` is a JSON object of the query parameters; headers are stored as JSON objects.
- `request_content` / `response_content` are the decoded bodies. `*_content_type` classifies each body as `BINARY` (not valid UTF-8, stored Base64-encoded), `JSON`, `XML`, `TEXT`, or `NULL` (no content available).
- Rows are written asynchronously after the response is received.

### Host ignore list

To avoid decrypting the same TLS hosts over and over, the addon keeps an `ignore_hosts` table (`address`, `created_at`, `last_seen_at`, `next_check_phase`) keyed by SNI (or the server address when there is no SNI):

- When a client completes a TLS handshake with mitmproxy, the host is inserted into `ignore_hosts`, or, if already present, its `last_seen_at` is refreshed and `next_check_phase` is incremented.
- On the next connection to a listed host, the TLS connection is passed through untouched (and therefore not recorded) until the interval for its phase has elapsed since `last_seen_at`: phase 1 is 1 minute, then 5 minutes, 30 minutes, 1 hour, 3 hours, 6 hours, 12 hours, 24 hours, and phase 9 is 48 hours. Beyond phase 9 the host is ignored indefinitely.
- When a client's TLS handshake with mitmproxy fails (for example because it does not trust the CA), the host is removed from `ignore_hosts`.
- Plain HTTP traffic is always recorded.

To make a host intercepted again, delete its row from `ignore_hosts`.

### Configuration

The addon reads these environment variables (set in `compose.yaml`):

| Variable | Required | Description |
|---|---|---|
| `DB_HOST` | yes | MySQL host |
| `DB_PORT` | no | MySQL port (default `3306`) |
| `DB_USER` | yes | MySQL user |
| `DB_PASSWORD` | yes | MySQL password |
| `DB_NAME` | yes | Database name |

### Database only

`docker compose -f compose-db.yaml up -d` starts only MySQL (without the schema auto-load) and phpMyAdmin.

### Schema export and import

The schema is managed with [sqldef](https://github.com/sqldef/sqldef) (`mysqldef`) through the image in `database/`:

```bash
# Dump the live schema to database/schema/mitm-packet-sniffer.sql
docker compose -f compose-export.yaml up

# Apply database/schema/mitm-packet-sniffer.sql to the database
docker compose -f compose-import.yaml up

# Show the changes without applying them
docker compose -f compose-import.yaml run --rm schema-import import-dry-run
```

Export and import both join the default network of this Compose project, so they work while `compose.yaml` or `compose-db.yaml` is running and the database is reachable as host `mysql`.

## Development

There is no test suite. CI (`.github/workflows/docker.yml`) builds the `mitmproxy-addon` image and runs a smoke test that starts the stack and fails if the `mitmproxy` container is not running or has restarted. See [`AGENTS.md`](AGENTS.md) for contributor guidance.
