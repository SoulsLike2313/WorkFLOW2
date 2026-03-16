# Public Repo Sanitization Report

- generated_at_utc: `2026-03-16T01:58:54.443798+00:00`
- scope: `public_audit_safe_rebuild`
- tracked_file_count: `1016`

## Removed From Tracking
- `setup_assets/windows10pro/SetupHost_strings.txt`
- `setup_assets/windows10pro/Strings.zip`
- `setup_assets/windows10pro/sdsbase.js`
- `setup_assets/windows10pro/strings_tool/Eula.txt`
- `setup_assets/windows10pro/windows10iso_page.html`

## Secret Scan
- status: `PASS`
- finding_count: `0`

## Absolute Path Scan
- status: `PASS_WITH_ALLOWED_EXAMPLES`
- hit_count: `2`
- note: remaining hits are non-secret examples/placeholders and not auth data.

## Publication Boundary
- policy: `docs/repo_publication_policy.md`
- target visibility: `public`
