# Static asset sample convention

This folder is reserved for **real or sanitized Linux static asset samples** used by FlexLM regression tests.

## Goal

Once samples are added, tests can validate the full static chain:

- license file parsing (`SERVER` / `VENDOR` / `FEATURE` / `INCREMENT` / `PACKAGE` / `UPGRADE` / `FEATURESET`)
- license log parsing (`OUT` / `IN` / `DENIED` / other event types)
- optional collector ingestion of `license_file_path` + `license_log_path`

## Layout

Create one subdirectory per vendor/server pair, for example:

- `synopsys_lic01/`
- `cadence_lic01/`
- `mentor_lic01/`
- `ansys_lic01/`

Each case directory may contain:

- `license.dat` — real or sanitized FlexLM license file
- `license.log` — real or sanitized FlexLM log file
- `manifest.json` — expectations for regression tests

## Example manifest.json

```json
{
  "server_name": "lic01",
  "vendor_name": "snpslmd",
  "expected_grants_min": 100,
  "expected_events_min": 50,
  "must_include_features": ["VCS_MX", "VCS_Runtime"],
  "must_include_event_types": ["OUT", "IN", "DENIED"]
}
```

## Notes

- Linux paths are the target runtime; Windows compatibility is not required here.
- Samples may be sanitized, but should preserve real syntax and structure.
- Prefer one reasonably representative sample per vendor before adding more edge cases.
