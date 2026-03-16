from app.services.flexlm_license_file_parser import FlexLMLicenseFileParser


def test_parse_license_file_records():
    raw_text = '''
SERVER lic01 001122334455 27000
VENDOR snpslmd /opt/synopsys/snpslmd options=/opt/synopsys/options.opt
FEATURE VCS_Runtime snpslmd 2024.12 31-dec-2026 10 ISSUED=01-jan-2024 NOTICE="core runtime"
INCREMENT VCS_MX snpslmd 2024.12 permanent 5 START=15-feb-2024 SN=ABC123
'''
    parser = FlexLMLicenseFileParser()

    parsed = parser.parse(raw_text)

    assert parsed.server is not None
    assert parsed.server.host == 'lic01'
    assert parsed.server.hostid == '001122334455'
    assert parsed.server.port == '27000'

    assert parsed.daemon is not None
    assert parsed.daemon.name == 'snpslmd'
    assert parsed.daemon.path == '/opt/synopsys/snpslmd'
    assert parsed.daemon.options_path == '/opt/synopsys/options.opt'

    assert len(parsed.grants) == 2
    assert parsed.grants[0].record_type == 'FEATURE'
    assert parsed.grants[0].feature_name == 'VCS_Runtime'
    assert parsed.grants[0].vendor_name == 'snpslmd'
    assert parsed.grants[0].quantity == 10
    assert parsed.grants[0].issued_date is not None
    assert parsed.grants[0].notice == 'core runtime'

    assert parsed.grants[1].record_type == 'INCREMENT'
    assert parsed.grants[1].feature_name == 'VCS_MX'
    assert parsed.grants[1].expiry_date is None
    assert parsed.grants[1].expiry_text == 'permanent'
    assert parsed.grants[1].serial_number == 'ABC123'


def test_parse_license_file_line_continuations():
    raw_text = '''
FEATURE PRIMEPOWER snpslmd 2024.12 31-dec-2026 20 \
    ISSUED=01-jan-2024 NOTICE="multi line"
'''
    parser = FlexLMLicenseFileParser()

    parsed = parser.parse(raw_text)

    assert len(parsed.grants) == 1
    assert parsed.grants[0].feature_name == 'PRIMEPOWER'
    assert parsed.grants[0].notice == 'multi line'
