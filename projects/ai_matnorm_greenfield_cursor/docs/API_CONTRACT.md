# API Contract v1

Base path: `/api/v1`

## Auth

```http
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET  /users/me
```

## Projects

```http
GET    /projects
POST   /projects
GET    /projects/{project_id}
PATCH  /projects/{project_id}
DELETE /projects/{project_id}
```

## Calculations

```http
POST   /calculations
GET    /calculations/{calculation_id}
PATCH  /calculations/{calculation_id}
POST   /calculations/{calculation_id}/revisions
GET    /calculations/{calculation_id}/revisions
```

## Files

```http
POST /files/upload
GET  /files/{file_id}
GET  /files/{file_id}/download
```

## Jobs

```http
POST /jobs/document-processing
GET  /jobs/{job_id}
GET  /jobs/{job_id}/events
GET  /jobs/{job_id}/stream
POST /jobs/{job_id}/pause
POST /jobs/{job_id}/resume
POST /jobs/{job_id}/cancel
```

## Documents/Facts

```http
GET   /documents/{document_id}
GET   /documents/{document_id}/facts
PATCH /facts/{fact_id}
POST  /facts/{fact_id}/confirm
POST  /facts/{fact_id}/reject
```

## KSI

```http
POST  /ksi/build
GET   /ksi/{calculation_id}
PATCH /ksi/nodes/{node_id}
POST  /ksi/nodes/{node_id}/children
```

## Materials

```http
GET  /materials
POST /materials
POST /materials/calculate
GET  /materials/results/{calculation_id}
```

## Templates/Exports

```http
POST /templates/excel
GET  /templates/excel
POST /exports/excel
GET  /exports/{export_id}/download
```

## Admin

```http
GET    /admin/users
POST   /admin/users
GET    /admin/ai-providers
POST   /admin/ai-providers
PATCH  /admin/ai-providers/{provider_id}
DELETE /admin/ai-providers/{provider_id}
POST   /admin/ai-providers/{provider_id}/test-connection
GET    /admin/token-usage
GET    /admin/jobs
GET    /admin/security-events
POST   /admin/seed-default-rules
```

## Templates mapping

```http
PATCH /templates/excel/{template_id}/mapping
```

## Reports

```http
GET /reports/{calculation_id}
```

## Monitoring

```http
GET /monitoring/status
```

## Settings (user)

```http
GET  /settings/ocr
POST /settings/ocr   # admin only
```

## Sync (desktop)

```http
POST /sync/events
GET  /sync/events
```
