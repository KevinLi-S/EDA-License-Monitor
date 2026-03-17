from pathlib import Path

from app.models import LicenseServer
from app.services.collector_service import CollectorService


def test_resolve_license_file_path_from_lmstat_output(tmp_path, monkeypatch):
    license_dir = tmp_path / 'license'
    license_dir.mkdir()
    license_file = license_dir / 'synopsys_lic01.dat'
    license_file.write_text('SERVER lic01 hostid 27000', encoding='utf-8')

    service = CollectorService()
    server = LicenseServer(name='Synopsys Main', vendor='synopsys', host='lic01', port=27000)
    raw_text = f'License file(s) on lic01: {license_file}:\n'

    assert service._resolve_license_file_path(server, raw_text=raw_text) == str(license_file)


def test_resolve_default_log_path_from_known_root(tmp_path, monkeypatch):
    license_dir = tmp_path / 'license'
    log_dir = license_dir / 'log'
    log_dir.mkdir(parents=True)
    log_file = log_dir / 'synopsys_lic01.log'
    log_file.write_text('10:05:00 (snpslmd) OUT: "VCS_MX" alice@ws01:0', encoding='utf-8')

    monkeypatch.setattr('app.services.collector_service.DEFAULT_LICENSE_DIR', license_dir)
    monkeypatch.setattr('app.services.collector_service.DEFAULT_LICENSE_LOG_DIR', log_dir)

    service = CollectorService()
    server = LicenseServer(name='Synopsys Main', vendor='synopsys', host='lic01', port=27000)

    assert service._resolve_license_log_path(server) == str(log_file)
