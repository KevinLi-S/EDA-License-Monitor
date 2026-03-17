from app.services.flexlm_parser import FlexLMParser


def test_parse_realistic_lmstat_checkout_detail_line():
    raw_text = '''
Users of Verdi:  (Total of 9999 licenses issued;  Total of 132 licenses in use)
 "Verdi" v2023.12, vendor: snpslmd, expiry: 31-dec-2026
 floating license
 user1 eda08 10.166.10.106:100 eda08user191214698 (v2020.06) (lic01/27010 225439), start Tue 2/24 10:54
'''
    parser = FlexLMParser()

    parsed = parser.parse(raw_text)

    assert parsed.status == 'down'
    assert len(parsed.features) == 1
    feature = parsed.features[0]
    assert feature.feature_name == 'Verdi'
    assert feature.total_licenses == 9999
    assert feature.used_licenses == 132
    assert len(feature.checkouts) == 1
    checkout = feature.checkouts[0]
    assert checkout.username == 'user1'
    assert checkout.hostname == 'eda08'
    assert checkout.display == '10.166.10.106:100'
    assert checkout.server_handle == 'lic01/27010 225439'
    assert 'eda08user191214698' in (checkout.process_info or '')
