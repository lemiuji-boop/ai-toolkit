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

"""Конвейер каталогизации: _INBOX → анализ → catalog."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.change_order import ChangeOrder
from app.models.change_order_directive import BacklogAction, ChangeOrderDirective, ImplementationKind
from app.models.document import Document, DocumentStatus
from app.models.inbox_pending import InboxPending
from app.models.record_revision import RevisionAction, RevisionTargetType
from app.services.revision_service import record_revision
from app.services.storage_access import NetworkStorage, StorageAccessMode, storage


def compute_file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_catalog_relative_path(product: str | None, doc_number: str) -> str:
    product_part = product or "_unknown"
    return f"{settings.catalog_subdir}/{product_part}/{doc_number}"


def detect_doc_kind(filename: str) -> str:
    low = filename.lower()
    if "ии" in low or "извещ" in low:
        return "ii"
    return "kd"


async def call_ai_analyze(file_path: str, doc_kind: str = "kd") -> dict:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.ai_agent_base_url}/analyze",
            json={"file_path": file_path, "doc_kind": doc_kind},
            headers={"X-API-Key": settings.ai_agent_api_key},
        )
        response.raise_for_status()
        return response.json()


def key_field_confidence(data: dict, doc_kind: str) -> float:
    if doc_kind == "ii":
        order = data.get("order_number", {})
        if isinstance(order, dict) and order.get("confidence"):
            return float(order["confidence"])
        directives = data.get("directives", [])
        if directives:
            return min(float(d.get("confidence", 0.5)) for d in directives)
        return 0.0

    keys = ("doc_number", "name")
    scores: list[float] = []
    for key in keys:
        field = data.get(key) or {}
        if isinstance(field, dict) and "confidence" in field:
            scores.append(float(field["confidence"]))
    return min(scores) if scores else 0.0


async def _ingest_change_order(
    db: AsyncSession,
    store: NetworkStorage,
    src: Path,
    data: dict,
    file_hash: str,
) -> dict:
    order_field = data.get("order_number", {})
    order_number = order_field.get("value") if isinstance(order_field, dict) else str(order_field)
    if not order_number:
        order_number = src.stem

    existing_co = await db.execute(
        select(ChangeOrder).where(
            ChangeOrder.order_number == order_number,
            ChangeOrder.deleted_at.is_(None),
        )
    )
    if existing_co.scalar_one_or_none():
        return {"status": "duplicate", "order_number": order_number, "file_hash": file_hash}

    rel_path = f"{settings.catalog_subdir}/_ИИ/{datetime.now(timezone.utc).year}/{order_number}"
    target_dir = store.root / rel_path
    store.mkdir(target_dir)
    target_file = target_dir / src.name
    store.move_file(src, target_file)

    change_order = ChangeOrder(
        order_number=order_number,
        file_path=str(target_file),
        description="Импорт из _INBOX",
    )
    db.add(change_order)
    await db.flush()

    for directive in data.get("directives", []):
        backlog_raw = directive.get("backlog_action")
        impl_kind_raw = directive.get("implementation_kind", "immediate")
        backlog_action = None
        if backlog_raw:
            try:
                backlog_action = BacklogAction(backlog_raw)
            except ValueError:
                backlog_action = None
        try:
            implementation_kind = ImplementationKind(impl_kind_raw)
        except ValueError:
            implementation_kind = ImplementationKind.immediate
        db.add(
            ChangeOrderDirective(
                change_order_id=change_order.id,
                affected_doc_number=directive.get("affected_doc_number"),
                backlog_action=backlog_action,
                implementation_kind=implementation_kind,
                implementation_product=directive.get("implementation_product"),
                directive_text=directive.get("directive_text"),
                confidence=directive.get("confidence"),
            )
        )

    await record_revision(
        db,
        target_type=RevisionTargetType.change_order,
        target_id=change_order.id,
        action=RevisionAction.create,
        changed_fields={"order_number": order_number},
        user=None,
    )
    return {"status": "ingested_ii", "change_order_id": change_order.id}


async def ingest_file(db: AsyncSession, file_path: str, storage_backend: NetworkStorage | None = None) -> dict:
    store = storage_backend or storage
    if store.check_access() != StorageAccessMode.READ_WRITE:
        return {"status": "skipped", "reason": "read_only_storage"}

    src = Path(file_path)
    if not src.exists():
        return {"status": "error", "reason": "file_not_found"}

    file_hash = compute_file_hash(src)
    existing = await db.execute(select(Document).where(Document.source_file_hash == file_hash))
    if existing.scalar_one_or_none():
        return {"status": "duplicate", "file_hash": file_hash}

    doc_kind = detect_doc_kind(src.name)
    try:
        analysis = await call_ai_analyze(str(src), doc_kind=doc_kind)
    except Exception as exc:  # noqa: BLE001
        from app.services.error_agent_service import handle_processing_failure

        await handle_processing_failure(
            db, context="разбор INBOX", error_text=str(exc), file_path=str(src), doc_kind=doc_kind
        )
        await db.commit()
        return {"status": "error", "reason": str(exc)}
    data = analysis.get("data", {})
    confidence = key_field_confidence(data, doc_kind)

    if confidence < settings.inbox_confidence_threshold:
        pending = InboxPending(
            file_path=str(src),
            file_hash=file_hash,
            status="needs_review",
            reason="low_confidence",
            confidence=confidence,
        )
        db.add(pending)
        await db.flush()
        return {"status": "needs_review", "confidence": confidence}

    if doc_kind == "ii":
        return await _ingest_change_order(db, store, src, data, file_hash)

    doc_number_field = data.get("doc_number", {})
    doc_number = doc_number_field.get("value") if isinstance(doc_number_field, dict) else str(doc_number_field)
    name_field = data.get("name", {})
    name = name_field.get("value") if isinstance(name_field, dict) else "Без наименования"
    product_field = data.get("product_number", {})
    product = product_field.get("value") if isinstance(product_field, dict) else None

    rel_path = build_catalog_relative_path(product, doc_number or src.stem)
    target_dir = store.root / rel_path
    store.mkdir(target_dir)
    target_file = target_dir / src.name
    store.move_file(src, target_file)

    document = Document(
        doc_number=doc_number or src.stem,
        name=name or src.stem,
        doc_type=data.get("doc_type", {}).get("value", "drawing") if isinstance(data.get("doc_type"), dict) else "drawing",
        status=DocumentStatus.active,
        product_number=product,
        catalog_path=rel_path,
        source_file_hash=file_hash,
        ocr_processed=True,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(document)
    await db.flush()
    await record_revision(
        db,
        target_type=RevisionTargetType.document,
        target_id=document.id,
        action=RevisionAction.create,
        changed_fields={"doc_number": document.doc_number, "catalog_path": rel_path},
        user=None,
    )
    return {"status": "ingested", "document_id": document.id, "catalog_path": rel_path}
