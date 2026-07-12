# Selective (Path-Based) CI/CD

Since the monorepo hosts four independent services, the production pipeline
(`.github/workflows/deploy.yml`) builds and deploys **only the services a
change actually affects**, instead of rebuilding everything on every push
to `main`.

## How a push to `main` is handled

1. **`detect-changes`** diffs the pushed range (`github.event.before` →
   `github.sha`) and classifies every changed file with
   [`deployment/scripts/detect-changes.sh`](../deployment/scripts/detect-changes.sh).
2. **`build-backend` / `build-ai` / `build-admin` / `build-landing`** run
   only for affected services. Each pushes `hairiq-<svc>:latest` and
   `hairiq-<svc>:<commit-sha>` to ECR, with a per-service Buildx cache scope.
3. **`deploy`** (serialized by the `production-deploy` concurrency group)
   syncs `server-deploy.sh` + the production compose files from the commit
   to the server, then runs via SSM:
   `server-deploy.sh <affected services...>`. The on-box script pulls and
   recreates **only those services** (`--no-deps`), runs Django migrations
   **only when backend is included**, and waits for the deployed containers
   to report healthy. An unhealthy service fails the deploy and the workflow.
4. **`summary`** writes the per-service affected/built/deployed table to the
   run summary — including the "nothing to deploy" case, which succeeds
   without building anything.

## Path rules

First matching rule wins (see `classify_path` in `detect-changes.sh` —
that file is the source of truth):

| Changed path | Effect |
|---|---|
| `services/backend/**` | backend |
| `services/ai/**` | ai |
| `services/admin/**` | admin |
| `services/landing/**` | landing |
| `deployment/environments/<svc>.env.example` | that service |
| `.github/workflows/deploy.yml`, `deployment/scripts/server-deploy.sh`, `deployment/scripts/detect-changes.sh`, `deployment/compose/docker-compose.base.yml`, `deployment/compose/production/**` | **all services** |
| `deployment/compose/local/**`, `deployment/compose/staging/**`, other `deployment/scripts/*`, other `.github/**`, `Makefile`, `docs/**`, `*.md`, `.gitignore`, IDE/agent dirs | nothing |
| `deployment/nginx/**`, `deployment/monitoring/**`, `infrastructure/**` | nothing in CI — apply with `make ansible-prod` / `make tf-apply`; the run summary reminds you |
| anything else (unknown) | **all services** (safe fallback) |

Unknown diff base (first push, force push) → **all services**.

## Manual deploys

`Actions → HairIQ CI/CD Pipeline → Run workflow` with the `services` input:
`all` (default) or a comma-separated subset, e.g. `backend,ai`. Manual runs
always **rebuild** the selected services at the current `main` commit before
deploying them (no git diff is consulted).

On the server: `server-deploy.sh backend ai`, `server-deploy.sh all` —
unknown or empty service names are rejected.

## Rollback

Images are built per service now, so an arbitrary old SHA may not exist for
every service. Roll back per service to the last tag that built it:

```bash
make rollback TAG=<sha>                       # all services
make rollback TAG=<sha> SERVICES="backend"    # one service
aws ecr describe-images --repository-name hairiq-backend \
  --query 'sort_by(imageDetails,&imagePushedAt)[-5:].imageTags'   # find tags
```

A missing image fails `docker compose pull` before any container is touched.

## Adding a new service

1. Add the compose service + env template, and the ECR repo.
2. Add it to `classify_path` and the outputs in `detect-changes.sh`.
3. Add a `build-<svc>` job in `deploy.yml`, list it in `deploy`'s `needs`
   and `if`, and in the `summary` job.
4. Add it to `VALID_SERVICES` in `server-deploy.sh` and `rollback.sh`.
