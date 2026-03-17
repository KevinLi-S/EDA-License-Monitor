import json
from pathlib import Path

from scripts.export_static_asset_samples import build_manifest, export_case, slugify


def test_slugify():
    assert slugify('Synopsys lic01') == 'synopsys_lic01'
    assert slugify('cadence-lic01.dat') == 'cadence_lic01_dat'


def test_build_manifest_and_export_case(tmp_path, monkeypatch):
    source_dir = tmp_path / 'license'
    source_dir.mkdir()

    license_path = source_dir / 'synopsys_lic01.dat'
    log_path = source_dir / 'synopsys_lic01.log'

    license_path.write_text(
        '\n'.join([
            'SERVER lic01 001122334455 27000',
            'VENDOR snpslmd /eda/env/license/snpslmd options=/eda/env/license/options.opt',
            'INCREMENT VCS_MX snpslmd 2025.03 31-dec-2026 20 START=15-feb-2024 SN=ABC123',
            'FEATURE VCS_Runtime snpslmd 2025.03 31-dec-2026 10 ISSUED=01-jan-2024',
        ]),
        encoding='utf-8',
    )
    log_path.write_text(
        '\n'.join([
            'TIMESTAMP 03/17/2026',
            '09:15:00 (snpslmd) OUT: "VCS_MX" alice@ws01:0',
            '09:20:12 (snpslmd) DENIED: "VCS_MX" bob@ws02:1 Licensed number of users already reached.',
        ]),
        encoding='utf-8',
    )

    manifest = build_manifest(license_path, log_path)
    assert manifest['server_name'] == 'lic01'
    assert manifest['vendor_name'] == 'snpslmd'
    assert manifest['expected_grants_min'] == 2
    assert 'VCS_MX' in manifest['must_include_features']
    assert manifest['expected_events_min'] == 2
    assert manifest['must_include_event_types'] == ['DENIED', 'OUT']

    monkeypatch.setattr(
        'scripts.export_static_asset_samples.choose_log_file',
        lambda case_name, source_dir: log_path,
    )

    output_dir = tmp_path / 'out'
    case_dir = export_case(license_path, output_dir)

    assert (case_dir / 'license.dat').exists()
    assert (case_dir / 'license.log').exists()
    saved_manifest = json.loads((case_dir / 'manifest.json').read_text(encoding='utf-8'))
    assert saved_manifest['server_name'] == 'lic01'
    assert saved_manifest['vendor_name'] == 'snpslmd'
