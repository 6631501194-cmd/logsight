# LogSight

LogSight is a PostgreSQL-backed, multi-tenant log ingestion system. Phase 1 provides a containerized FastAPI API, PostgreSQL persistence, JSON ingestion authenticated by tenant-scoped API keys, normalization, Alembic migrations, and a working UDP Syslog forwarding collector.

## Local startup

1. Copy `.env.example` to `.env` and replace every `CHANGE_ME` value with strong local values. Keep `.env` uncommitted.
2. Start the complete appliance stack:

   ```sh
   docker compose up --build -d
   ```

3. Confirm services:

   ```sh
   curl http://localhost:8000/health
   curl http://localhost:5173
   ```

4. Send a JSON log (the request `tenant` value is intentionally ignored; the API key determines ownership):

   ```sh
   curl -i -X POST http://localhost:8000/ingest \
     -H "Content-Type: application/json" \
     -H "X-Ingestion-Key: $BOOTSTRAP_INGESTION_KEY" \
     --data @samples/api-login-failed.json
   ```

5. Inspect persistence:

   ```sh
   docker compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
     -c 'SELECT tenant_id, source, event_type, src_ip, raw FROM logs;'
   ```

6. Test UDP Syslog ingestion (macOS):

   ```sh
   logger -n 127.0.0.1 -P 5514 -d 'vendor=demo action=deny src=10.0.1.10'
   docker compose logs syslog-collector
   ```

## Development commands

`docker compose config` validates the stack. `docker compose logs -f backend` shows migrations and API errors. `docker compose down -v` removes local database data; do not use it where data must be retained.

Run backend unit tests in the container with:

```sh
docker compose run --rm --no-deps -e PYTHONPATH=/app --entrypoint pytest backend /app/tests -q
```

## Security model

Each `IngestionKey` is SHA-256 hashed at rest and belongs to one active `Tenant`. `POST /ingest` requires `X-Ingestion-Key`; its tenant is taken from that database key, never from user JSON. Raw payloads are retained in PostgreSQL JSONB.
