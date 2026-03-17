from datetime import UTC, datetime

from app.services.flexlm_log_parser import FlexLMLogParser


def test_parse_log_events_out_in_denied():
    raw_text = '''
09:15:00 (snpslmd) OUT: "VCS_Runtime" alice@ws01
09:16:30 (snpslmd) IN: "VCS_Runtime" alice@ws01
09:20:12 (snpslmd) DENIED: "VCS_MX" bob@ws02:0.0
'''
    parser = FlexLMLogParser()

    parsed = parser.parse(raw_text, reference_date=datetime(2026, 3, 16, 0, 0, tzinfo=UTC))

    assert [event.event_type for event in parsed.events] == ['OUT', 'IN', 'DENIED']
    assert parsed.events[0].feature_name == 'VCS_Runtime'
    assert parsed.events[0].username == 'alice'
    assert parsed.events[0].hostname == 'ws01'
    assert parsed.events[2].display == '0.0'
    assert parsed.events[1].event_time is not None
    assert parsed.events[1].event_time.hour == 9
    assert len({event.event_hash for event in parsed.events}) == 3


def test_parse_log_events_with_timestamp_date_markers():
    raw_text = '''
TIMESTAMP 03/16/2026
09:15:00 (snpslmd) OUT: "VCS_Runtime" alice@ws01
TIMESTAMP 03/17/2026
00:05:00 (snpslmd) DENIED: "VCS_MX" bob@ws02:0.0 Licensed number of users already reached.
'''
    parser = FlexLMLogParser()

    parsed = parser.parse(raw_text, reference_date=datetime(2026, 3, 15, 0, 0, tzinfo=UTC))

    assert len(parsed.events) == 2
    assert parsed.events[0].event_time == datetime(2026, 3, 16, 9, 15, 0, tzinfo=UTC)
    assert parsed.events[1].event_time == datetime(2026, 3, 17, 0, 5, 0, tzinfo=UTC)
    assert parsed.events[1].event_type == 'DENIED'
    assert parsed.events[1].username == 'bob'
