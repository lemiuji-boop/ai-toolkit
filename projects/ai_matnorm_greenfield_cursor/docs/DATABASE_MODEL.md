# Database Model

## Core entities

```text
users
roles
permissions
user_roles
projects
calculations
calculation_revisions
files
documents
pages
extracted_facts
spec_rows
assembly_links
ksi_nodes
materials
material_aliases
kim_rules
allowance_rules
aux_material_rules
process_rules
calculation_items
calculation_summaries
excel_templates
excel_exports
reports
jobs
job_events
assistant_messages
assistant_questions
user_corrections
learning_examples
ai_providers
ai_models
ai_requests
api_key_secrets
audit_logs
security_events
sync_events
```

## Critical invariants

1. Files are immutable after upload.
2. Approved calculation revisions are immutable.
3. User corrections never overwrite original extracted facts; they create corrected versions.
4. AI responses are logged with provider/model/tokens/status, but secrets are never logged.
5. Every exported Excel file is linked to template version and calculation revision.
6. Every material calculation stores formula, input facts, rules and user overrides.
