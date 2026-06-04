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

"""ORM-модели."""

from app.models.analytics import AnalyticsEvent
from app.models.assets import Asset, Prompt
from app.models.characters import Character
from app.models.compliance import ComplianceReport, QualityReport
from app.models.episodes import Episode, Scene, Shot
from app.models.enums import (
    AssetType,
    EpisodeStatus,
    GenerationTaskStatus,
    PublicationStatus,
)
from app.models.locations import Location
from app.models.projects import BrandProfile, MonetizationLink, Project
from app.models.publications import Publication
from app.models.tasks import GenerationTask

__all__ = [
    "AnalyticsEvent",
    "Asset",
    "AssetType",
    "BrandProfile",
    "Character",
    "ComplianceReport",
    "Episode",
    "EpisodeStatus",
    "GenerationTask",
    "GenerationTaskStatus",
    "Location",
    "MonetizationLink",
    "Project",
    "Prompt",
    "Publication",
    "PublicationStatus",
    "QualityReport",
    "Scene",
    "Shot",
]
