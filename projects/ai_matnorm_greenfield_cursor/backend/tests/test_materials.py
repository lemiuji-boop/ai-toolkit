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

"""FR-052: детерминированный расчёт материалов."""
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Calculation, KsiNode, Project, User, UserStatus
from app.services.material_calculator import calculate_materials


@pytest.mark.asyncio
async def test_calculate_materials_formula(db_session: AsyncSession):
    uid = uuid.uuid4()
    user = User(
        id=uid,
        email="t@t.com",
        full_name="T",
        password_hash="x",
        status=UserStatus.ACTIVE,
    )
    proj = Project(id=uuid.uuid4(), name="P", owner_id=uid)
    calc = Calculation(id=uuid.uuid4(), project_id=proj.id, title="C", created_by_id=uid)
    node = KsiNode(
        id=uuid.uuid4(),
        calculation_id=calc.id,
        designation="DET-1",
        name="Деталь",
        node_type="detail",
        quantity_total=2.0,
    )
    db_session.add_all([user, proj, calc, node])
    await db_session.flush()
    items = await calculate_materials(db_session, calc.id)
    assert len(items) >= 1
    assert "gross" in items[0].formula.lower()
