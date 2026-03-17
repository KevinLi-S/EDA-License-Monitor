import json
from pathlib import Path

import pytest

from app.services.flexlm_license_file_parser import FlexLMLicenseFileParser
from app.services.flexlm_log_parser import FlexLMLogParser


STATIC_SAMPLES_DIR = Path(__file__).resolve().parent.parent / 'samples' / 'static_assets'


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw.decode('utf-16', errors='ignore')
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('latin-1', errors='ignore')


def _load_cases() -> list[Path]:
    if not STATIC_SAMPLES_DIR.exists():
        return []
    return sorted(
        path for path in STATIC_SAMPLES_DIR.iterdir()
        if path.is_dir() and (path / 'manifest.json').exists() and (path / 'license.dat').exists()
    )


CASES = _load_cases()


@pytest.mark.skipif(not CASES, reason='No real static asset sample cases have been added yet.')
@pytest.mark.parametrize('case_dir', CASES, ids=[path.name for path in CASES])
def test_parse_real_static_asset_samples(case_dir: Path):
    manifest = json.loads((case_dir / 'manifest.json').read_text(encoding='utf-8'))

    license_parser = FlexLMLicenseFileParser()
    license_text = _read_text(case_dir / 'license.dat')
    parsed_license = license_parser.parse(license_text)

    assert parsed_license.server is not None
    assert parsed_license.daemon is not None
    assert parsed_license.server.host == manifest['server_name']
    assert parsed_license.daemon.name == manifest['vendor_name']
    assert len(parsed_license.grants) >= manifest.get('expected_grants_min', 1)

    for feature_name in manifest.get('must_include_features', []):
        assert any(grant.feature_name == feature_name for grant in parsed_license.grants)

    log_path = case_dir / 'license.log'
    if log_path.exists():
        log_parser = FlexLMLogParser()
        parsed_log = log_parser.parse(_read_text(log_path))

        assert len(parsed_log.events) >= manifest.get('expected_events_min', 1)
        for event_type in manifest.get('must_include_event_types', []):
            assert any(event.event_type == event_type for event in parsed_log.events)
