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

"""FR-060–FR-061: Excel export с mapping."""
from app.services.excel_templates.export import export_materials_to_excel


def test_export_with_mapping():
    mapping = {
        "sheet": "Лист1",
        "start_row": 3,
        "columns": {
            "designation": "A",
            "material": "B",
            "net_qty": "C",
            "gross_qty": "D",
            "unit": "E",
        },
    }
    rows = [{"designation": "X-1", "material_name": "Сталь", "net_qty": 1, "gross_qty": 2, "unit": "kg"}]
    data = export_materials_to_excel(None, rows, field_mapping=mapping)
    assert len(data) > 1000
    assert data[:2] == b"PK"
