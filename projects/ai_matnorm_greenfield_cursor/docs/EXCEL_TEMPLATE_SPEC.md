# Excel Template Specification

## Goal

The system must fill user-provided Excel templates without destroying formatting.

## Template registration

Admin uploads `.xlsx` template and creates mapping:

```json
{
  "template_name": "Ведомость норм материалов",
  "sheet": "Лист1",
  "start_row": 10,
  "columns": {
    "position": "A",
    "designation": "B",
    "name": "C",
    "material": "D",
    "unit": "E",
    "net_qty": "F",
    "gross_qty": "G",
    "kim": "H",
    "note": "I"
  }
}
```

## Export rules

- Preserve styles where possible.
- Preserve formulas outside generated ranges.
- Add generated rows using style of template row.
- Save export as immutable artifact.
- Link export to calculation revision.
