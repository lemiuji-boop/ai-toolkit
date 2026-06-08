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

"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-22

"""
from typing import Sequence, Union

from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Полная схема из SQLAlchemy metadata
    from app.db import models  # noqa: F401
    from app.db.base import Base

    bind = op.get_bind()
    Base.metadata.create_all(bind)


def downgrade() -> None:
    from app.db import models  # noqa: F401
    from app.db.base import Base

    bind = op.get_bind()
    Base.metadata.drop_all(bind)
