# Copyright 2026 Rinat Ishmaev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

.PHONY: infra api worker web smoke

infra:
	docker compose -f infra/docker-compose.yml up -d

migrate:
	cd services/api && .venv/bin/alembic upgrade head

api:
	cd services/api && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	cd services/api && .venv/bin/celery -A app.celery_app worker --loglevel=info

web:
	npm run dev:web

smoke:
	bash scripts/smoke.sh
