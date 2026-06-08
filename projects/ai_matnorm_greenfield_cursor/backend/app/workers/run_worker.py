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

"""Точка входа RQ worker (полная реализация — этап 4)."""
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Worker stub: полный RQ worker подключается на этапе 4")
    try:
        from app.workers.rq_app import run_worker

        run_worker()
    except ImportError:
        logger.warning("RQ worker ещё не настроен — ожидание...")
        import time

        while True:
            time.sleep(60)


if __name__ == "__main__":
    main()
