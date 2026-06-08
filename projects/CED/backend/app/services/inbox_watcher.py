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

"""Watchdog-наблюдатель за папкой _INBOX."""

from __future__ import annotations

import logging
import threading

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.core.config import settings
from app.services.storage_access import StorageAccessMode, storage
from app.tasks.inbox_tasks import ingest_file_task

logger = logging.getLogger(__name__)


class InboxHandler(FileSystemEventHandler):
    def on_created(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.is_directory:
            return
        path = str(event.src_path)
        if path.startswith("."):
            return
        ingest_file_task.delay(path)


_observer: Observer | None = None


def start_inbox_watcher() -> None:
    global _observer
    if not settings.enable_inbox_watcher:
        return
    if storage.check_access() != StorageAccessMode.READ_WRITE:
        logger.warning("INBOX watcher не запущен: каталог READ_ONLY")
        return

    inbox = storage.inbox_path()
    inbox.mkdir(parents=True, exist_ok=True)

    handler = InboxHandler()
    _observer = Observer()
    _observer.schedule(handler, str(inbox), recursive=False)
    thread = threading.Thread(target=_observer.start, daemon=True)
    thread.start()
    logger.info("INBOX watcher запущен: %s", inbox)
