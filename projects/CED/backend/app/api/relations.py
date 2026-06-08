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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.models.user import User

router = APIRouter()


def _build_tree(nodes: list[dict], root_id: int) -> dict:
    index: dict[int, dict] = {}
    for row in nodes:
        node_id = int(row["id"])
        index[node_id] = {
            "id": node_id,
            "doc_number": row["doc_number"],
            "name": row["name"],
            "children": [],
        }

    for row in nodes:
        parent_id = row.get("parent_id")
        if parent_id is not None and int(parent_id) in index and int(row["id"]) in index:
            index[int(parent_id)]["children"].append(index[int(row["id"])])

    if root_id not in index:
        raise HTTPException(status_code=404, detail="Document not found")
    return index[root_id]


@router.get("/documents/{document_id}/relations")
async def get_relations_tree(
    document_id: int,
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> dict:
    query = text(
        """
        WITH RECURSIVE relation_tree AS (
            SELECT d.id, d.doc_number, d.name, NULL::int AS parent_id, 0 AS depth, ARRAY[d.id] AS path
            FROM documents d
            WHERE d.id = :document_id

            UNION ALL

            SELECT child.id, child.doc_number, child.name, rel.parent_id, rt.depth + 1, rt.path || child.id
            FROM relation_tree rt
            JOIN document_relations rel ON rel.parent_id = rt.id
            JOIN documents child ON child.id = rel.child_id
            WHERE rt.depth < 10 AND NOT child.id = ANY(rt.path)
        )
        SELECT id, doc_number, name, parent_id, depth
        FROM relation_tree
        ORDER BY depth, id
        """
    )
    result = await db.execute(query, {"document_id": document_id})
    rows = [dict(row._mapping) for row in result.fetchall()]
    return _build_tree(rows, document_id)
