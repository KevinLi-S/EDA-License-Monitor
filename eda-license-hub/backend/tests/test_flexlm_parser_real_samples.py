from pathlib import Path

from app.services.flexlm_parser import FlexLMParser


SAMPLES_DIR = Path(__file__).resolve().parent.parent / 'samples' / 'lmstat'


def _read_sample(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw.decode('utf-16', errors='ignore')
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('latin-1', errors='ignore')


def test_parse_real_lmstat_samples_regression():
    parser = FlexLMParser()
    expectations = {
        'ansys_lic01_real.txt': {'feature_count': 1405, 'vendors': {'ansyslmd': 'up'}, 'license_path': '/eda/env/license/ansys_lic01.dat'},
        'cadence_lic01_real.txt': {'feature_count': 3287, 'vendors': {'cdslmd': 'up'}, 'license_path': '/eda/env/license/cadence_lic01.dat'},
        'mentor_lic01_real.txt': {'feature_count': 2179, 'vendors': {'saltd': 'up', 'mgcld': 'up'}, 'license_path': '/eda/env/license/mentor_lic01.dat'},
        'synopsys_lic01_real.txt': {'feature_count': 7794, 'vendors': {'snpslmd': 'up'}, 'license_path': '/eda/env/license/synopsys_lic01.dat'},
    }

    for sample_name, expected in expectations.items():
        raw_text = _read_sample(SAMPLES_DIR / sample_name)
        snapshot = parser.parse(raw_text)

        assert snapshot.status == 'up', sample_name
        assert len(snapshot.features) == expected['feature_count'], sample_name
        assert raw_text.find(expected['license_path']) != -1, sample_name
        for vendor_name, vendor_status in expected['vendors'].items():
            assert snapshot.vendor_status.get(vendor_name) == vendor_status, sample_name

        assert snapshot.features[0].feature_name
        assert snapshot.features[0].total_licenses >= snapshot.features[0].used_licenses
