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

"""Нагрузочный сценарий для health и каталога (требует запущенный backend)."""

from locust import HttpUser, between, task


class CedUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self) -> None:
        response = self.client.post(
            "/auth/login",
            json={"login": "admin", "password": "admin"},
        )
        if response.ok:
            token = response.json().get("access_token")
            self.client.headers["Authorization"] = f"Bearer {token}"

    @task(3)
    def health(self) -> None:
        self.client.get("/health")

    @task(2)
    def catalog(self) -> None:
        self.client.get("/catalog?page=1&size=20")
