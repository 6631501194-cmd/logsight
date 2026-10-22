# Free deployment guide: Neon + Render + Vercel

This guide deploys the existing LogSight web application without publishing PostgreSQL, ingestion keys, passwords, or JWT secrets. It intentionally does **not** deploy the UDP Syslog collector; use HTTP ingestion for the public demo.

## Before you begin

1. Push this repository to GitHub. Verify that `.env` and any `.env.*` secret files are absent from the GitHub file list. `.env.example` is a template only.
2. Create strong, different production values for every password, ingestion key, and `JWT_SECRET`. Keep them in a password manager or an untracked local file.
3. Use the public demo accounts only for the recruiter-facing application. Do not reuse personal passwords.

## 1. Create the Neon PostgreSQL database

1. Create a Neon account and a new free PostgreSQL project.
2. Copy the connection string from Neon. Enable its required TLS/SSL option (Neon connection strings normally include `sslmode=require`).
3. Keep the connection string private. Do not put it in the repository, Vercel, or the browser.
4. In Render, set this value as `DATABASE_URL`. Both of these forms work with LogSight:

   ```text
   postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
   postgresql+psycopg://USER:PASSWORD@HOST/DATABASE?sslmode=require
   ```

   LogSight normalizes the first form to Psycopg 3 automatically.

Neon is the only database host. Do not create a public PostgreSQL service or add a public database port.

## 2. Deploy the FastAPI API to Render

The root `render.yaml` defines a free Python web service named `logsight-api`. It installs `backend/requirements.txt`, runs `alembic upgrade head` immediately before starting Uvicorn on Render's assigned `$PORT`, and uses `/health` as its health check. This startup form is used because Render Free does not support pre-deploy commands.

1. In Render, connect GitHub and select this repository.
2. Choose **New > Blueprint** and select the `main` branch. Render detects `render.yaml` at the repository root.
3. Create the Blueprint, then enter the environment variables below in the Render dashboard. Values marked **secret** must never be committed.
4. Deploy. Wait for the `/health` check to pass and copy the public API URL, for example `https://logsight-api.onrender.com`.
5. Open `https://YOUR-RENDER-URL/health`. Expect an HTTP 200 response.

### Render environment variables

| Variable | Value / purpose | Secret |
|---|---|---|
| `DATABASE_URL` | Neon TLS connection string | Yes |
| `JWT_SECRET` | Long random signing secret | Yes |
| `BACKEND_CORS_ORIGINS` | Your Vercel URL, for example `https://logsight.vercel.app` | No |
| `BOOTSTRAP_TENANT_SLUG` | `demo` | No |
| `BOOTSTRAP_TENANT_NAME` | `Demo Tenant` | No |
| `BOOTSTRAP_ADMIN_EMAIL` | Recruiter demo admin email for `demo` | No |
| `BOOTSTRAP_ADMIN_PASSWORD` | Bootstrap admin password | Yes |
| `BOOTSTRAP_INGESTION_KEY` | Tenant-scoped API ingestion key | Yes |
| `DEMO_A_ADMIN_EMAIL` | DemoA admin email | No |
| `DEMO_A_ADMIN_PASSWORD` | DemoA admin password | Yes |
| `DEMO_A_VIEWER_EMAIL` | DemoA viewer email | No |
| `DEMO_A_VIEWER_PASSWORD` | DemoA viewer password | Yes |
| `DEMO_A_INGESTION_KEY` | DemoA HTTP ingestion key | Yes |
| `DEMO_B_ADMIN_EMAIL` | DemoB admin email | No |
| `DEMO_B_ADMIN_PASSWORD` | DemoB admin password | Yes |
| `DEMO_B_VIEWER_EMAIL` | DemoB viewer email | No |
| `DEMO_B_VIEWER_PASSWORD` | DemoB viewer password | Yes |
| `DEMO_B_INGESTION_KEY` | DemoB HTTP ingestion key | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | No |
| `RETENTION_DAYS` | `7` | No |
| `RETENTION_CHECK_INTERVAL_SECONDS` | `86400` | No |

On startup, LogSight idempotently creates the `demo`, `demoA`, and `demoB` tenants, their users, tenant-scoped ingestion-key hashes, and the failed-login alert rules. It does not overwrite logs.

## 3. Apply and verify migrations

Render runs `alembic upgrade head` immediately before the API starts. Confirm its successful migration output in the Render deployment log before sharing the URL.

Render Free does not provide Dashboard Shell access. If you need an independent migration check before deploying, run this locally from a secured environment that contains the same production variables and Neon `DATABASE_URL`:

```bash
cd /path/to/logsight
set -a
source /safe/path/production-logsight.env
set +a
cd backend
alembic current
alembic heads
```

After the first migration, both commands should report revision `0002_alert_dedupe` as the current/head revision. Do not run `alembic downgrade` against the demo database.

## 4. Create production demo logs safely

The application startup creates users and alert rules. Sample logs are created separately through the authenticated HTTP ingestion path by `samples/generate_demo_data.py`.

On your own machine, create an **untracked** file with the same required production variables as Render, load it, and point the script at your deployed API:

```bash
cd /path/to/logsight
set -a
source /safe/path/production-logsight.env
set +a
LOGSIGHT_API_URL=https://YOUR-RENDER-URL python3 samples/generate_demo_data.py
```

Expected first run: `demoA: created=20` and `demoB: created=12`. A later run skips existing `seed_id` values, so it does not duplicate the sample dataset. Never place `production-logsight.env` inside the Git repository.

## 5. Deploy the React frontend to Vercel

1. In Vercel, import the same GitHub repository.
2. Set **Root Directory** to `frontend`.
3. Leave the framework preset as Vite. The project uses `npm run build` and outputs `dist`.
4. Set this Vercel environment variable for Production, Preview, and Development as appropriate:

   | Variable | Value |
   |---|---|
   | `VITE_API_BASE_URL` | `https://YOUR-RENDER-URL` |

5. Deploy and copy the Vercel URL.
6. Update Render's `BACKEND_CORS_ORIGINS` to exactly that URL (no trailing path), then redeploy Render.
7. Open the Vercel URL, log in with a production demo account, and verify Dashboard, Log explorer, and Alerts.

`frontend/vercel.json` supplies an SPA rewrite so direct visits to `/login`, `/logs`, and `/alerts` load the React application. `VITE_API_BASE_URL` is bundled into public frontend JavaScript, so it must contain only the public API URL—never an ingestion key, database URL, password, or JWT secret.

## Public demo credentials

Share only the deliberately-created viewer account with a recruiter where possible. Provide its email and password privately (for example, in the recruiter message), never in GitHub, source files, issue trackers, or this guide. Do not share ingestion keys.

## Deployment order and final checks

1. Neon database created.
2. Render variables configured and API deployed.
3. Confirm `/health` and migration revision.
4. Generate the idempotent sample logs through the authenticated seed script.
5. Vercel deployed with `VITE_API_BASE_URL` set to Render.
6. Render CORS updated with the final Vercel URL and API redeployed.
7. Test a viewer login, tenant-scoped dashboard, log search, and alert list.

## Free-tier considerations

Free plans and quotas change. Verify current provider limits before sharing the public URL. In particular, free Render web services can sleep when idle, so the first request may take longer, and free instances do not include Shell access or pre-deploy commands. For an internship demo this is usually acceptable; open the API health URL shortly before the recruiter tests it.

## Official documentation

- [Neon connection strings](https://neon.com/docs/connect/connect-from-any-app)
- [Render Blueprints](https://render.com/docs/infrastructure-as-code)
- [Render Blueprint specification](https://render.com/docs/blueprint-spec)
- [Vercel environment variables](https://vercel.com/docs/environment-variables)
