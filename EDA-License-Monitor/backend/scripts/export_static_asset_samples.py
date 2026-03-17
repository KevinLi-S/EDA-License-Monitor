import argparse
import json
import shutil
from pathlib import Path

from app.services.flexlm_license_file_parser import FlexLMLicenseFileParser
from app.services.flexlm_log_parser import FlexLMLogParser


DEFAULT_SOURCE_DIR = Path('/eda/env/license')
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / 'samples' / 'static_assets'
LOG_DIR_CANDIDATES = [DEFAULT_SOURCE_DIR / 'log', DEFAULT_SOURCE_DIR]
LICENSE_SUFFIXES = {'.dat', '.lic', '.txt'}
LOG_SUFFIXES = {'.log', '.txt'}


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw.decode('utf-16', errors='ignore')
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('latin-1', errors='ignore')


def slugify(value: str) -> str:
    return ''.join(ch.lower() if ch.isalnum() else '_' for ch in value).strip('_')


def find_license_files(source_dir: Path) -> list[Path]:
    return sorted(path for path in source_dir.iterdir() if path.is_file() and path.suffix.lower() in LICENSE_SUFFIXES)


def choose_log_file(case_name: str, source_dir: Path) -> Path | None:
    tokens = {token for token in case_name.split('_') if token}
    candidates: list[Path] = []
    for root in LOG_DIR_CANDIDATES:
        if not root.exists():
            continue
        for path in root.iterdir():
            if not path.is_file() or path.suffix.lower() not in LOG_SUFFIXES:
                continue
            stem = slugify(path.stem)
            if all(token in stem for token in tokens if token not in {'license', 'lic'}):
                candidates.append(path)
    return sorted(candidates)[0] if candidates else None


def build_manifest(license_path: Path, log_path: Path | None) -> dict:
    license_parser = FlexLMLicenseFileParser()
    parsed_license = license_parser.parse(read_text(license_path))

    manifest = {
        'server_name': parsed_license.server.host if parsed_license.server else '',
        'vendor_name': parsed_license.daemon.name if parsed_license.daemon else '',
        'expected_grants_min': len(parsed_license.grants),
        'must_include_features': sorted({grant.feature_name for grant in parsed_license.grants[:20] if grant.feature_name})[:10],
    }

    if log_path and log_path.exists():
        log_parser = FlexLMLogParser()
        parsed_log = log_parser.parse(read_text(log_path))
        manifest['expected_events_min'] = len(parsed_log.events)
        manifest['must_include_event_types'] = sorted({event.event_type for event in parsed_log.events if event.event_type})
    else:
        manifest['expected_events_min'] = 0
        manifest['must_include_event_types'] = []

    return manifest


def export_case(license_path: Path, output_dir: Path) -> Path:
    case_name = slugify(license_path.stem)
    case_dir = output_dir / case_name
    case_dir.mkdir(parents=True, exist_ok=True)

    target_license = case_dir / 'license.dat'
    shutil.copy2(license_path, target_license)

    log_path = choose_log_file(case_name, license_path.parent)
    if log_path:
        shutil.copy2(log_path, case_dir / 'license.log')

    manifest = build_manifest(target_license, case_dir / 'license.log' if (case_dir / 'license.log').exists() else None)
    (case_dir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    return case_dir


def main() -> None:
    parser = argparse.ArgumentParser(description='Export real static FlexLM assets into regression sample cases.')
    parser.add_argument('--source-dir', type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    exported: list[Path] = []
    for license_path in find_license_files(args.source_dir):
        exported.append(export_case(license_path, args.output_dir))

    for path in exported:
        print(f'exported {path}')
    print(f'total={len(exported)}')


if __name__ == '__main__':
    main()
