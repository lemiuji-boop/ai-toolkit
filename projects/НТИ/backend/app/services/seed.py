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

"""Первичное наполнение БД."""

from sqlalchemy.orm import Session

from app.db.models import AdminUser, ApiService, MobileUser, OllamaModel, SystemSetting
from app.services.security import hash_password

DEFAULT_OPERATIONS = [
    "Токарная",
    "Фрезерная",
    "Сверлильная",
    "Шлифовальная",
    "Сборочная",
    "Обивочная",
    "Покраска",
    "Контрольная",
]


def seed_database(db: Session) -> None:
    if db.query(AdminUser).count() == 0:
        db.add(AdminUser(username="admin", password_hash=hash_password("admin123")))

    demo_users = [
        ("ivanov", "demo123", "Иванов Иван Иванович", "1001"),
        ("petrov", "demo123", "Петров Пётр Петрович", "1002"),
    ]
    for username, password, display_name, tab_number in demo_users:
        if db.query(MobileUser).filter(MobileUser.username == username).first() is None:
            db.add(
                MobileUser(
                    username=username,
                    password_hash=hash_password(password),
                    display_name=display_name,
                    tab_number=tab_number,
                )
            )

    if db.query(ApiService).count() == 0:
        db.add_all(
            [
                ApiService(
                    name="Ollama (локальный)",
                    base_url="http://127.0.0.1:11434",
                    description="LLM для подсказок и анализа",
                    enabled=True,
                ),
                ApiService(
                    name="Внешний REST API",
                    base_url="https://api.example.com",
                    api_key="",
                    description="Интеграция с корпоративным API",
                    enabled=False,
                ),
            ]
        )

    if db.query(OllamaModel).count() == 0:
        db.add_all(
            [
                OllamaModel(model_name="llama3.2:3b", is_active=True, notes="Быстрая модель"),
                OllamaModel(model_name="qwen2.5:7b", is_active=False, notes="Точнее, тяжелее"),
                OllamaModel(model_name="mistral:7b", is_active=False),
            ]
        )

    defaults = {
        "ollama_base_url": "http://127.0.0.1:11434",
        "active_ollama_model": "llama3.2:3b",
        "mobile_public_url": "http://10.0.2.2:8010",
    }
    for key, value in defaults.items():
        if db.get(SystemSetting, key) is None:
            db.add(SystemSetting(key=key, value=value))

    db.commit()
