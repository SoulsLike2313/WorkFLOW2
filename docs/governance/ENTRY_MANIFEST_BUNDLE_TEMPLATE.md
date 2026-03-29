# ENTRY_MANIFEST_BUNDLE_TEMPLATE

Status:
- template_version: `v1`
- usage: `Astartes -> Primarch entry declaration`

---

## 1) Header

- manifest_id:
- timestamp_utc:
- astartes_node_id:
- department_binding_id:
- issuer_rank:
- issuer_mode:

## 2) Hardware Profile

- cpu:
- ram_gb:
- storage_total_gb:
- storage_free_gb:
- accelerator_gpu:

## 3) Software Profile

- os:
- python_version:
- node_version:
- package_managers:
- vcs_tools:

## 4) Tooling Profile

- build_tools:
- test_tools:
- lint_static_tools:
- export_bundle_tools:

## 5) Runtime Capability

- parallel_capacity:
- long_run_stability_note:
- known_runtime_limits:

## 6) Stack Readiness

| stack_item | readiness (`READY/PARTIAL/MISSING`) | note |
| --- | --- | --- |
| python |  |  |
| javascript/typescript |  |  |
| data/analytics tools |  |  |
| ci-like local checks |  |  |

## 7) Availability and Load

- current_load_class (`LOW/MEDIUM/HIGH`):
- available_hours_window:
- blackout_windows:

## 8) Speed Profile

- small_task_turnaround:
- medium_task_turnaround:
- heavy_task_turnaround:

## 9) Risks and Trust Note

- known_risks:
- trust_note:
- confidence_level:

## 10) Evidence References

- command_outputs_or_logs:
- artifact_paths:
- validation_refs:

## 11) Acceptance

- primarch_review_status:
- accepted_for_assignment (`yes/no`):
- review_comment:

